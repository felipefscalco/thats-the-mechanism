#!/usr/bin/env python3
"""r8 hook step: 3-5 candidate hooks per episode with mixed patterns, hard rules in code, a rubric judge, payoff check.

  hooks.py gen   <slug> [--n 5] [--dry-run]   role `hooks` writes candidates; code rules filter; role `hook_judge` scores
                                               the survivors on a rubric; best one is chosen ->
                                               episodes/<slug>/hooks.json, hooks.md (review), script.hook.txt (proposal)
  hooks.py check <slug> [--json]               rules on the CURRENT script.txt opening (used by qa.py / preview.py)
  hooks.py apply <slug>                        script.hook.txt -> script.txt. The script gate (pipeline.config.json
                                               gates.script) then blocks TTS until the new script is approved.
Patterns (each `gen` must cover at least 3 of them): curiosity_gap, pattern_interrupt (visual), specific_question,
contrarian (careful: true and sourced, never a fake 'everyone is wrong'). Rules live HERE, not in the prompt:
banned intro padding / clickbait, word limits, a curiosity-gap signal in the first sentence, and the promise must be paid
off later in the script (quote found in the script after the hook). Ideas from public hook guides (scrollmark hook-anatomy,
video-hook-generator); nothing vendored."""
import argparse, difflib, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from script_text import spoken

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "pipeline.config.json").read_text()).get("hooks", {})
MAX_SPOKEN = CFG.get("max_spoken_words", 16)
MAX_ONSCREEN = CFG.get("max_onscreen_words", 6)
PATTERNS = ("curiosity_gap", "pattern_interrupt", "specific_question", "contrarian")
BANNED = [  # (regex, why)
    (r"\bhey (guys|everyone|folks)\b", "intro padding"), (r"\bwhat'?s up\b", "intro padding"),
    (r"\btoday,? (i|we)('ll| will| are going to| am going to| want to)\b", "intro padding"),
    (r"\bin (this|today'?s) (video|short|episode)\b", "intro padding"), (r"\bwelcome (back )?to\b", "intro padding"),
    (r"\b(let me|i'?ll|i will) (show|tell|explain)\b", "intro padding"), (r"\bdon'?t forget to\b", "intro padding"),
    (r"\bwait,? don'?t scroll\b", "clickbait"), (r"\b(you|you'?ll) won'?t believe\b", "clickbait"),
    (r"\bsecrets?\b", "clickbait"), (r"\bshocking\b", "clickbait"), (r"\b(nobody|no one) (is )?(talking|tells you)\b", "clickbait"),
    (r"\b(watch|stay) (till|until|to) the end\b", "clickbait"), (r"\bthis will blow your mind\b", "clickbait"),
    (r"\bmind[- ]?blowing\b", "clickbait"), (r"\b(insane|crazy) (trick|hack)\b", "clickbait"), (r"\b99 ?% of people\b", "clickbait"),
]
GAP_WORDS = r"\b(barely|almost|never|not|isn'?t|aren'?t|doesn'?t|don'?t|wrong|opposite|backwards|actually|without|only|nothing|same|both|invisible|impossible|strange|weird|why|how|what|where|until|instead|still|even|missing|lost|lose|gone|disappears?|vanish(?:es)?|hidden)\b"
_SENT = re.compile(r"(?<=[.!?])\s+")
_STOP = set("the a an of to and is are was it its it's in on at for by with that this these those you your be as from or so".split())

def first_sentence(text): return _SENT.split(spoken(text).strip(), 1)[0].strip()

def banned(text):
    return [f"{why}: '{m.group(0)}'" for rx, why in BANNED for m in [re.search(rx, text, re.I)] if m]

def curiosity(sentence):
    """Heuristic curiosity-gap signals in ONE sentence (the LLM judge checks the same thing semantically)."""
    s = sentence.lower(); sig = []
    if s.rstrip().endswith("?"): sig.append("question")
    if re.search(GAP_WORDS, s): sig.append("tension word")
    if re.search(r"\b\d[\d,.]*\b|\b(thousand|million|billion|hundred|twice|half|dozens?)\b", s): sig.append("specific number")
    if re.search(r"\bthe \w+(?: \w+)? (that|which|who) \w+", s): sig.append("paradox title ('the X that Y')")
    if re.search(r"\b(made of|is really|is actually|is just|turns out)\b", s): sig.append("reframe")
    if re.search(r"\b(itself|themselves|on its own|by itself)\b", s): sig.append("impossible agency")
    if re.search(r"\b(\w{3,}) (with|against|into|from) \1\b", s): sig.append("paradox repetition ('X with X')")
    explains = bool(re.search(r"\bbecause\b|\bwhich means\b|\bthat'?s why\b", s))
    return dict(ok=bool(sig) and not explains, signals=sig, explains_too_early=explains)

def content_words(t): return {w for w in re.findall(r"[a-z']+", t.lower()) if w not in _STOP and len(w) > 3}

def quote_in(script_after, quote, thr=0.85):
    q = " ".join(quote.lower().split()); s = " ".join(script_after.lower().split())
    if not q: return 0.0
    if q in s: return 1.0
    n = len(q); best = 0.0
    for i in range(0, max(1, len(s) - n + 1), max(1, n // 6)):
        best = max(best, difflib.SequenceMatcher(None, q, s[i:i + n]).ratio())
    return round(best, 3)

def rule_check(c, script):
    """Hard rules for one candidate (dict with line, on_screen, pattern, promise, payoff_quote)."""
    body = spoken(script); rest = body.split(first_sentence(script), 1)[-1]
    f = []
    f += banned(c.get("line", "") + " " + c.get("on_screen", ""))
    nw = len(c.get("line", "").split()); no = len(c.get("on_screen", "").split())
    if nw > MAX_SPOKEN: f.append(f"spoken hook {nw} words > {MAX_SPOKEN}")
    if no > MAX_ONSCREEN: f.append(f"first on-screen line {no} words > {MAX_ONSCREEN}")
    if not no: f.append("no first on-screen line")
    cur = curiosity(first_sentence(c.get("line", "")))
    if not cur["ok"]: f.append("no curiosity-gap signal in the first sentence" + (" (explains too early)" if cur["explains_too_early"] else ""))
    pq = quote_in(rest, c.get("payoff_quote", ""))
    if pq < 0.85: f.append(f"payoff quote not found later in the script (best match {pq})")
    elif not (content_words(c.get("promise", "")) & content_words(rest)): f.append("promise shares no key term with the payoff")
    if c.get("pattern") not in PATTERNS: f.append(f"unknown pattern {c.get('pattern')}")
    return dict(ok=not f, failures=f, curiosity=cur, payoff_match=pq)

GEN_SCHEMA = {"type": "object", "required": ["candidates"], "properties": {"candidates": {"type": "array", "minItems": 3, "maxItems": 5, "items": {
    "type": "object", "required": ["pattern", "line", "on_screen", "frame1_visual", "promise", "payoff_quote"], "properties": {
        "pattern": {"type": "string", "enum": list(PATTERNS)}, "line": {"type": "string"}, "on_screen": {"type": "string"},
        "frame1_visual": {"type": "string"}, "promise": {"type": "string"}, "payoff_quote": {"type": "string"}}}}}}
JUDGE_SCHEMA = {"type": "object", "required": ["scores"], "properties": {"scores": {"type": "array", "items": {"type": "object",
    "required": ["index", "curiosity_gap", "specificity", "visual_hook", "payoff", "honesty", "gap_in_first_sentence", "note"], "properties": {
        "index": {"type": "integer"}, "curiosity_gap": {"type": "integer"}, "specificity": {"type": "integer"}, "visual_hook": {"type": "integer"},
        "payoff": {"type": "integer"}, "honesty": {"type": "integer"}, "gap_in_first_sentence": {"type": "boolean"}, "note": {"type": "string"}}}}}}
WEIGHTS = dict(curiosity_gap=0.3, payoff=0.25, visual_hook=0.2, specificity=0.15, honesty=0.1)

def _ctx(slug):
    E = ROOT / "episodes" / slug
    read = lambda n: (E / n).read_text() if (E / n).exists() else ""
    return E, read("script.txt"), read("VIDEO.md")[:3000], read("facts.json")[:2500]

def gen(slug, n=5, dry=False):
    import llm
    E, script, video, facts = _ctx(slug)
    tpl = (ROOT / "prompts" / "hooks.md").read_text()
    prompt = tpl.format(SLUG=slug, N=n, SCRIPT=spoken(script), VIDEO=video or "(none)", FACTS=facts or "(none)", MAX_SPOKEN=MAX_SPOKEN,
                        MAX_ONSCREEN=MAX_ONSCREEN, BANNED="; ".join(sorted({rx.replace('\\b', '') for rx, _ in BANNED})), PATTERNS=", ".join(PATTERNS))
    logd = ROOT / "qa" / "hooks" / slug; logd.mkdir(parents=True, exist_ok=True)
    r = llm.run("hooks", prompt, workdir=ROOT, schema=GEN_SCHEMA, read_only=True, dry_run=dry, log_dir=logd)
    if dry: print(json.dumps(r.get("meta", {}), indent=1)); return
    cands = (r.get("json") or {}).get("candidates") or []
    if len(cands) < 3: sys.exit(f"hooks: role returned {len(cands)} candidates ({r.get('meta', {}).get('error')})")
    pats = {c.get("pattern") for c in cands}
    for c in cands: c["rules"] = rule_check(c, script)
    ok = [i for i, c in enumerate(cands) if c["rules"]["ok"]]
    jt = (ROOT / "prompts" / "hook_judge.md").read_text().format(SCRIPT=spoken(script), CANDIDATES=json.dumps(
        [dict(index=i, **{k: c[k] for k in ("pattern", "line", "on_screen", "frame1_visual", "promise", "payoff_quote")}) for i, c in enumerate(cands)], indent=1))
    j = llm.run("hook_judge", jt, workdir=ROOT, schema=JUDGE_SCHEMA, read_only=True, log_dir=logd)
    for s in (j.get("json") or {}).get("scores", []):
        if 0 <= s.get("index", -1) < len(cands):
            s["weighted"] = round(sum(WEIGHTS[k] * s[k] for k in WEIGHTS), 2); cands[s["index"]]["judge"] = s
    # judge veto: a hook the judge says has no gap in its first sentence fails the LLM half of the curiosity gate
    elig = [i for i in ok if cands[i].get("judge", {}).get("gap_in_first_sentence", True)]
    pick = max(elig, key=lambda i: cands[i].get("judge", {}).get("weighted", 0), default=None)
    cur = dict(line=first_sentence(script), rules=rule_check(dict(line=first_sentence(script), on_screen="(current)", pattern="curiosity_gap",
               promise=first_sentence(script), payoff_quote=""), script))
    out = dict(slug=slug, patterns_covered=sorted(p for p in pats if p), candidates=cands, chosen=pick, current_opening=cur["line"],
               providers=dict(hooks=r.get("meta", {}).get("provider"), hook_judge=j.get("meta", {}).get("provider")),
               cost_usd=round((r.get("meta", {}).get("cost_usd") or 0) + (j.get("meta", {}).get("cost_usd") or 0), 4))
    if len(out["patterns_covered"]) < 3: out["warning"] = "fewer than 3 hook patterns covered"
    (E / "hooks.json").write_text(json.dumps(out, indent=1))
    md = [f"# Hooks — {slug}", "", f"Current opening: _{cur['line']}_", ""]
    for i, c in enumerate(cands):
        jd = c.get("judge", {})
        md += [f"## {'✅ CHOSEN — ' if i == pick else ''}{i}. {c['pattern']}", f"- spoken: **{c['line']}**", f"- first on-screen line: `{c['on_screen']}`",
               f"- frame 1: {c['frame1_visual']}", f"- promise → payoff: {c['promise']} → “{c['payoff_quote']}” (match {c['rules']['payoff_match']})",
               f"- rules: {'PASS' if c['rules']['ok'] else 'FAIL — ' + '; '.join(c['rules']['failures'])} · curiosity signals: {', '.join(c['rules']['curiosity']['signals']) or 'none'}",
               f"- judge: {jd.get('weighted', '—')} (gap {jd.get('curiosity_gap')}, payoff {jd.get('payoff')}, visual {jd.get('visual_hook')}, specific {jd.get('specificity')}, honest {jd.get('honesty')}) — {jd.get('note', '')}", ""]
    (E / "hooks.md").write_text("\n".join(md))
    if pick is not None:
        body = script.strip(); fs = first_sentence(script)
        (E / "script.hook.txt").write_text(body.replace(fs, cands[pick]["line"].strip(), 1) + "\n") if fs in body else None
    print(f"hooks {slug}: {len(cands)} candidates, {len(ok)} pass rules, chosen={pick}", (cands[pick]["line"] if pick is not None else "(none)"))

def check(slug, as_json=False):
    """Rules on the CURRENT opening: banned phrases, curiosity signal, spoken length; payoff via hooks.json if chosen there."""
    E, script, *_ = _ctx(slug); fs = first_sentence(script); f = banned(" ".join(_SENT.split(spoken(script))[:2]))
    cur = curiosity(fs)
    if not cur["ok"]: f.append("no curiosity-gap signal in the first sentence")
    if len(fs.split()) > MAX_SPOKEN: f.append(f"first sentence {len(fs.split())} words > {MAX_SPOKEN}")
    hj = json.loads((E / "hooks.json").read_text()) if (E / "hooks.json").exists() else None
    payoff = None
    if hj and hj.get("chosen") is not None:
        c = hj["candidates"][hj["chosen"]]
        if " ".join(c["line"].split()) == " ".join(fs.split()) or c["line"].strip().startswith(fs):
            payoff = c["rules"]["payoff_match"]
            if not c["rules"]["ok"]: f += c["rules"]["failures"]
            if c.get("judge", {}).get("gap_in_first_sentence") is False: f.append("judge: no curiosity gap in the first sentence")
    res = dict(ok=not f, first_sentence=fs, failures=f, curiosity=cur, payoff_match=payoff, hooks_json=bool(hj))
    if as_json: print(json.dumps(res))
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["gen", "check", "apply"]); ap.add_argument("slug")
    ap.add_argument("--n", type=int, default=5); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.cmd == "gen": gen(a.slug, a.n, a.dry_run)
    elif a.cmd == "check":
        r = check(a.slug, a.json)
        if not a.json: print("hook check", a.slug, "PASS" if r["ok"] else "FAIL", r["failures"], r["curiosity"]["signals"])
        sys.exit(0 if r["ok"] else 1)
    else:
        E = ROOT / "episodes" / a.slug; p = E / "script.hook.txt"
        if not p.exists(): sys.exit("no script.hook.txt: run hooks.py gen first")
        (E / "script.txt").write_text(p.read_text()); print("script.txt updated; TTS stays blocked until: scripts/gates.py approve", a.slug, "script --by <name> --artifact episodes/%s/script.txt" % a.slug)
