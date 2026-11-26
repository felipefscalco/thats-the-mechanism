#!/usr/bin/env python3
"""r8 publish pack: everything a human needs to post an episode, and NOTHING is posted (design approved by Felipe;
docs/QUEUE_AND_PUBLISH.md).

  publish.py pack   <CompId> <slug> [--suf v8] [--mp4 PATH] [--no-llm]   -> publish/<slug>/
  publish.py verify <slug>                                                re-check limits/credits of an existing pack
  publish.py upload <slug> --platform tiktok|youtube_shorts|instagram_reels [--dry-run]
                    STUB: refuses unless publish/<slug>/APPROVED holds this pack's sha; even then it refuses in r8
                    (no uploader is implemented). Every attempt is logged with its request_id.

Pack contents (publish/<slug>/):
  video.mp4    copy of the final render (gitignored)
  pack.json    per-platform title / caption / hashtags within platform limits, YouTube synthetic-media disclosure,
               made_for_kids=false, credits + sources, request_id per platform, pack_sha
  review.md    what Felipe reads before approving: the three posts, limits, credits, checklist, approve command
  uploads.jsonl  append-only log of upload attempts (request_id idempotency: a request_id logged as "posted" is never retried)
Approval: Felipe creates publish/<slug>/APPROVED containing the pack_sha line printed in review.md. Any change to the pack
changes the sha and voids the approval."""
import argparse, hashlib, json, re, shutil, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from script_text import spoken
import credits as credits_mod
import hooks as hooks_mod

ROOT = Path(__file__).resolve().parent.parent
REGEN = False
LIMITS = {  # title chars / caption chars / max hashtags (r8 brief)
    "tiktok": dict(title=100, caption=2200, hashtags=5),
    "youtube_shorts": dict(title=100, caption=5000, hashtags=3),
    "instagram_reels": dict(title=125, caption=2200, hashtags=8),
}
BRAND_TAGS = ["#ThatsTheMechanism", "#Science", "#HowItWorks", "#Shorts", "#Physics", "#Engineering", "#STEM", "#LearnOnTikTok"]

def cut(s, n):
    s = " ".join(str(s).split())
    if len(s) <= n: return s
    s = s[: n - 1].rsplit(" ", 1)[0].rstrip(",;:-–")
    return s + "…"

def tagify(t):
    t = re.sub(r"[^\w]", "", str(t).lstrip("#"))
    return f"#{t}" if t else ""

def platform_post(p, base, tags):
    L = LIMITS[p]
    title = cut(base["title"], L["title"])
    seen, ht = set(), []
    lead = (["#Shorts"] if p == "youtube_shorts" else []) + ["#ThatsTheMechanism"]          # YouTube: #Shorts first; other platforms never get it
    for t in lead + [tagify(x) for x in tags] + BRAND_TAGS:
        if not t or t.lower() in seen or len(ht) >= L["hashtags"]: continue
        if t.lower() == "#shorts" and p != "youtube_shorts": continue
        seen.add(t.lower()); ht.append(t)
    body = base["caption"].strip()
    credit_line = base.get("credit_line", "")
    tail = "\n\n" + " ".join(ht)
    room = L["caption"] - len(tail) - (len("\n\n" + credit_line) if credit_line else 0)
    caption = cut(body, room) + (("\n\n" + credit_line) if credit_line else "") + tail
    post = dict(title=title, caption=caption, hashtags=ht,
                lengths=dict(title=len(title), caption=len(caption), hashtags=len(ht)), limits=L)
    if p == "youtube_shorts":
        # Altered/synthetic content disclosure: synthetic voice + generated visuals -> disclose (conservative default)
        post.update(synthetic_media=True, made_for_kids=False, category="Education", visibility="private_until_approved")
    if p == "tiktok": post.update(ai_generated_content_label=True)
    if p == "instagram_reels": post.update(ai_info_label=True)
    return post

def violations(pack):
    v = []
    for p, post in pack["platforms"].items():
        L = LIMITS[p]
        if len(post["title"]) > L["title"]: v.append(f"{p}: title {len(post['title'])} > {L['title']}")
        if len(post["caption"]) > L["caption"]: v.append(f"{p}: caption {len(post['caption'])} > {L['caption']}")
        if len(post["hashtags"]) > L["hashtags"]: v.append(f"{p}: {len(post['hashtags'])} hashtags > {L['hashtags']}")
        if hooks_mod.banned(post["title"] + " " + post["caption"]): v.append(f"{p}: clickbait/padding {hooks_mod.banned(post['title'] + ' ' + post['caption'])}")
    yt = pack["platforms"].get("youtube_shorts", {})
    if yt.get("made_for_kids") is not False or yt.get("synthetic_media") is not True: v.append("youtube: made_for_kids must be false and synthetic_media true")
    for p in credits_mod.scan(json.dumps(pack["credits"]) + json.dumps(pack["platforms"])): v.append(f"credits/captions: {p}")
    return v

def sha(b): return hashlib.sha256(b).hexdigest()

def draft_text(slug, script, title_hint, use_llm):
    first = hooks_mod.first_sentence(script)
    base = dict(title=title_hint or first.rstrip("."), caption=" ".join(spoken(script).split("\n\n")[0].split()) + " The mechanism, in under a minute.", tags=[])
    if not use_llm: return base, None
    import llm
    schema = {"type": "object", "required": ["title", "caption", "tags"], "properties": {"title": {"type": "string"}, "caption": {"type": "string"},
              "tags": {"type": "array", "items": {"type": "string"}}}}
    prompt = (ROOT / "prompts" / "publisher.md").read_text().format(SCRIPT=spoken(script), TITLE=title_hint or "", BANNED="; ".join(sorted({rx.replace('\\b', '') for rx, _ in hooks_mod.BANNED})))
    r = llm.run("publisher", prompt, workdir=ROOT, schema=schema, read_only=True, log_dir=ROOT / "qa" / "publish" / slug)
    j = r.get("json") or {}
    if j.get("title") and j.get("caption") and not hooks_mod.banned(j["title"] + " " + j["caption"]):
        base.update(title=j["title"], caption=j["caption"], tags=j.get("tags", [])[:8])
    return base, r.get("meta", {})

def pack(comp, slug, suf, mp4, use_llm):
    E = ROOT / "episodes" / slug; out = ROOT / "publish" / slug; out.mkdir(parents=True, exist_ok=True)
    mp4 = Path(mp4) if mp4 else ROOT / "renders" / f"{comp}_{suf}.mp4"
    if not mp4.exists(): sys.exit(f"no render at {mp4}")
    script = (E / "script.txt").read_text()
    title_hint = next((r["text"][0] for r in __import__("shotlib").shots(slug)[:1] if r["text"]), None) if (E / "shots.md").exists() else None
    nice = lambda t: " ".join(w.lower() if w.lower() in ("of", "the", "a", "an", "and", "to", "in", "on", "with") and i else w[:1].upper() + w[1:].lower() for i, w in enumerate(t.split()))
    prev = json.loads((out / "pack.json").read_text()) if (out / "pack.json").exists() else {}
    if prev.get("draft") and not REGEN:   # stable text across re-packs: the LLM drafts once; --regen-text to redraft
        base, meta = dict(prev["draft"]), prev.get("llm")
    else:
        base, meta = draft_text(slug, script, nice(title_hint) if title_hint else None, use_llm)
    # credits: sanitized photo credits + source pages (public URLs only)
    rows = []
    cp = ROOT / "assets" / "photos" / "CREDITS.csv"
    if cp.exists():
        import csv
        rows = [credits_mod.credit_record(r) for r in csv.DictReader(open(cp)) if r.get("episode") == slug]
    src = json.loads((E / "facts.json").read_text()).get("sources", []) if (E / "facts.json").exists() else []
    sources = [dict(title=s.get("title", ""), url=credits_mod.safe_public_url(s.get("url")) or "") for s in src]
    credit_line = ("Images: " + "; ".join(f"{r['author']} ({r['license']})" for r in rows)) if rows else ""
    base = dict(base); base["credit_line"] = cut(credit_line, 300) if credit_line else ""
    vsha = sha(mp4.read_bytes())
    shutil.copy(mp4, out / "video.mp4")
    plats = {p: platform_post(p, base, base.get("tags", [])) for p in LIMITS}
    p = dict(episode=slug, composition=comp, render=str(mp4.relative_to(ROOT)) if mp4.is_relative_to(ROOT) else mp4.name,
             video_sha256=vsha, created=time.strftime("%Y-%m-%dT%H:%M:%S%z"), platforms=plats,
             credits=dict(images=[{k: r[k] for k in ("title", "author", "license", "source_url", "license_url")} for r in rows], sources=sources),
             draft={k: base[k] for k in ("title", "caption", "tags")},
             llm=dict(provider=(meta or {}).get("provider"), cost_usd=(meta or {}).get("cost_usd")) if meta else None,
             approval=dict(required=True, file=f"publish/{slug}/APPROVED", status="pending"), upload="not implemented (r8): stub refuses")
    body = json.dumps({k: p[k] for k in ("episode", "video_sha256", "platforms", "credits")}, sort_keys=True).encode()
    p["pack_sha"] = sha(body)[:16]
    for name, post in plats.items():  # idempotency key per post: same video + same text = same request_id
        post["request_id"] = sha(f"{slug}|{name}|{vsha}|{post['title']}|{post['caption']}".encode())[:20]
    p["violations"] = violations(p)
    (out / "pack.json").write_text(json.dumps(p, indent=1, ensure_ascii=False))
    (out / "review.md").write_text(review_md(p))
    print(f"pack {slug}: {out}/pack.json sha={p['pack_sha']} violations={len(p['violations'])}")
    return 0 if not p["violations"] else 1

def review_md(p):
    L = [f"# Publish review — {p['episode']}", "", f"Video: `publish/{p['episode']}/video.mp4` (sha256 {p['video_sha256'][:12]}…, from `{p['render']}`)",
         f"Pack sha: **{p['pack_sha']}**", "", "Nothing has been posted. Upload is not implemented in r8.", ""]
    for name, post in p["platforms"].items():
        L += [f"## {name}", f"- title ({post['lengths']['title']}/{post['limits']['title']}): **{post['title']}**",
              f"- hashtags ({post['lengths']['hashtags']}/{post['limits']['hashtags']}): {' '.join(post['hashtags'])}",
              f"- caption ({post['lengths']['caption']}/{post['limits']['caption']}):", "", "```", post["caption"], "```"]
        if name == "youtube_shorts": L += [f"- altered/synthetic content disclosure: **{post['synthetic_media']}** · made for kids: **{post['made_for_kids']}** · visibility: {post['visibility']}"]
        if name == "tiktok": L += [f"- AI-generated content label: **{post['ai_generated_content_label']}**"]
        if name == "instagram_reels": L += [f"- AI info label: **{post['ai_info_label']}**"]
        L += [f"- request_id: `{post['request_id']}`", ""]
    imgs = [f"- {c['title']} — {c['author']} — {c['license']} — {c['source_url']}" for c in p["credits"]["images"]] or ["- (no photos)"]
    srcs = [f"- {s['title']} {s['url']}" for s in p["credits"]["sources"]] or ["- (none listed)"]
    L += ["## Credits", *imgs, "", "## Sources", *srcs, "",
          "## Checks", *([f"- ❌ {v}" for v in p["violations"]] or ["- ✅ limits, disclosure flags, credits (no tokens / local paths), no clickbait"]), "",
          "## Before approving", "- [ ] watched the video.mp4 end to end with sound", "- [ ] titles and captions are accurate (no overclaim)",
          "- [ ] credits are complete", "", "To approve this exact pack (any change voids it):", "", "```",
          f"echo {p['pack_sha']} > publish/{p['episode']}/APPROVED", "```", ""]
    return "\n".join(L)

def upload(slug, platform, dry):
    d = ROOT / "publish" / slug; pj = d / "pack.json"
    if not pj.exists(): sys.exit("no pack: run publish.py pack first")
    p = json.loads(pj.read_text()); post = p["platforms"][platform]; rid = post["request_id"]
    led = d / "uploads.jsonl"; hist = [json.loads(l) for l in led.read_text().splitlines()] if led.exists() else []
    def logit(status, why):
        with led.open("a") as f: f.write(json.dumps(dict(t=time.strftime("%Y-%m-%dT%H:%M:%S%z"), platform=platform, request_id=rid, pack_sha=p["pack_sha"], status=status, reason=why)) + "\n")
        print(f"upload {slug} {platform}: {status} — {why} (request_id {rid})")
    if any(h["request_id"] == rid and h["status"] == "posted" for h in hist):
        logit("skipped_duplicate", "this request_id was already posted"); return 0
    ap_ = d / "APPROVED"
    if not ap_.exists(): logit("refused", "no APPROVED file (Felipe must create it)"); return 3
    if p["pack_sha"] not in ap_.read_text().split(): logit("refused", "APPROVED does not match this pack_sha (pack changed after approval)"); return 3
    if p.get("violations"): logit("refused", f"pack has violations: {p['violations'][:3]}"); return 3
    logit("refused", "approved, but no uploader is implemented in r8 (stub)"); return 4

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["pack", "verify", "upload"]); ap.add_argument("a"); ap.add_argument("b", nargs="?")
    ap.add_argument("--suf", default="v2"); ap.add_argument("--mp4"); ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--platform", choices=list(LIMITS)); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--regen-text", action="store_true")
    x = ap.parse_args(); REGEN = x.regen_text
    if x.cmd == "pack": sys.exit(pack(x.a, x.b, x.suf, x.mp4, not x.no_llm))
    if x.cmd == "verify":
        p = json.loads((ROOT / "publish" / x.a / "pack.json").read_text()); v = violations(p); print("verify", x.a, "PASS" if not v else v); sys.exit(1 if v else 0)
    if not x.platform: ap.error("--platform required")
    sys.exit(upload(x.a, x.platform, x.dry_run))
