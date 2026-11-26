#!/usr/bin/env python3
"""r8 pipeline CLI: batch topic queue + --stop-at + preflight (design approved by Felipe; docs/QUEUE_AND_PUBLISH.md).

  pipeline.py --batch topics.jsonl [--stop-at STAGE] [--only SLUG] [--retry-failed] [--dry-run]
  pipeline.py --preflight [--stop-at STAGE]          checks only (exit 2 if anything needed is missing)
  pipeline.py --status [--batch topics.jsonl]        table of per-topic state

Stages, in order (--stop-at = last stage to run; default ship):
  plan     scaffold the episode if needed (new-episode.sh); role `writer` drafts script.txt + brief.md from title/angle
           when script.txt is still the template                                                   [LLM]
  hooks    scripts/hooks.py gen: 3-5 hooks, code rules, rubric judge; chosen hook goes into the draft script  [LLM]
  script   facts gate (facts.py check) + script gate (gates.py require script): a human gate -> topic WAITS
  audio    Kokoro TTS (pause tags) -> loudnorm -> script-aligned captions -> mix -> durations.json
  preview  build_loop.py --until preview: planner VIDEO.md, builder, still-only gates loop          [LLM]
  ship     build_loop.py --until judge: one full render + all gates + pairwise/calibrated judge, then
           scripts/publish.py pack (approval-gated pack, NO upload)                                 [LLM]
Topic file: JSON list or JSONL, one object per topic: {"title", "angle", "priority", "approved"} (+ optional "slug",
"id", "pillar", "prev"). approved != true -> skipped. Higher priority runs first; ties keep file order.
State: queue/state/<slug>.json (status pending|running|waiting|done|failed|skipped, stages_done, history, last_error),
written after every stage, so a rerun resumes at the first stage not done. One failing topic never blocks the others.
Preflight runs BEFORE any LLM call and only checks what the requested stages need (CLIs per role chain, ffmpeg/ffprobe,
node/npx, venv, Kokoro + whisper.cpp models, CLI logins as present/absent - never printing a secret)."""
import argparse, json, os, re, shutil, subprocess, sys, time, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm

ROOT = llm.ROOT
PY = str(ROOT / ".venv-tts/bin/python") if (ROOT / ".venv-tts/bin/python").exists() else sys.executable
STAGES = ["plan", "hooks", "script", "audio", "preview", "ship"]
LLM_ROLES = {"plan": ["writer"], "hooks": ["hooks", "hook_judge"], "preview": ["planner", "builder", "fixer"],
             "ship": ["builder", "critic", "critic_deep", "critic_tiebreak", "clusterer"]}
STATE_DIR = ROOT / "queue" / "state"

class Waiting(Exception): """a human gate is closed; not a failure"""

# ---------------------------------------------------------------- topics
def load_topics(path):
    p = Path(path); txt = p.read_text()
    items = json.loads(txt) if txt.lstrip().startswith("[") else [json.loads(l) for l in txt.splitlines() if l.strip() and not l.lstrip().startswith("//")]
    out = []
    for k, t in enumerate(items):
        miss = [f for f in ("title", "angle", "priority", "approved") if f not in t]
        if miss: raise SystemExit(f"{path}: topic {k + 1} missing {miss}")
        t = dict(t); t["_order"] = k
        t.setdefault("slug", None); t.setdefault("pillar", "sci")
        out.append(t)
    return sorted(out, key=lambda t: (-float(t["priority"]), t["_order"]))

def kebab(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40].strip("-")
_NEW = []
def resolve(t):
    if not t.get("slug"):
        existing = {d.name.split("-", 1)[1]: d.name for d in (ROOT / "episodes").iterdir() if d.is_dir() and "-" in d.name}
        base = kebab(t["title"])
        if base in existing: t["slug"] = existing[base]
        elif t.get("approved") is not True: t["slug"] = f"xx-{base}"   # skipped topics don't consume an episode number
        else:
            _NEW.append(base); t["slug"] = f"{len([d for d in (ROOT / 'episodes').iterdir() if d.is_dir()]) + len(_NEW):02d}-{base}"
    if not t.get("id"):
        t["id"] = "".join(w.capitalize() for w in re.findall(r"[a-z0-9]+", t["slug"].split("-", 1)[1])[:2]) or "Ep"
    return t

# ---------------------------------------------------------------- state
def load_state(slug):
    p = STATE_DIR / f"{slug}.json"
    return json.loads(p.read_text()) if p.exists() else dict(slug=slug, status="pending", stages_done=[], history=[], attempts=0)
def save_state(s):
    STATE_DIR.mkdir(parents=True, exist_ok=True); p = STATE_DIR / f"{s['slug']}.json"
    tmp = p.with_suffix(".tmp"); tmp.write_text(json.dumps(s, indent=1)); os.replace(tmp, p)
def log(s, stage, status, **kw):
    s["history"].append(dict(t=time.strftime("%Y-%m-%dT%H:%M:%S%z"), stage=stage, status=status, **kw)); save_state(s)
    print(f"[{s['slug']}] {stage}: {status} {json.dumps(kw)[:200] if kw else ''}", flush=True)

# ---------------------------------------------------------------- preflight
def preflight(stop_at):
    need = STAGES[: STAGES.index(stop_at) + 1]; probs, info = [], {}
    roles = sorted({r for st in need for r in LLM_ROLES.get(st, [])})
    for r in roles:
        try:
            spec = llm.role_spec(r); chain = [spec] + list(spec.get("fallback", []))
        except Exception as e:
            probs.append(f"role {r}: {e}"); continue
        ok = [c["provider"] for c in chain if llm.available(c["provider"])]
        info[f"role:{r}"] = ok[0] if ok else None
        if not ok: probs.append(f"role {r}: no provider CLI installed in its chain {[c['provider'] for c in chain]}")
    used = {v for k, v in info.items() if k.startswith("role:") and v}
    if "claude" in used:
        tf = Path(os.path.expanduser(os.environ.get("TTM_CLAUDE_TOKEN_FILE", "~/.secrets/claude_oauth_token")))
        logged = bool(os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")) or tf.is_file()
        if not logged:
            r = subprocess.run(["claude", "auth", "status"], capture_output=True, text=True, timeout=30)  # output never printed
            logged = r.returncode == 0 and "not logged" not in (r.stdout + r.stderr).lower()
        info["login:claude"] = logged
        if not logged: probs.append("claude: no token (CLAUDE_CODE_OAUTH_TOKEN / TTM_CLAUDE_TOKEN_FILE) and not logged in")
    if "agy" in used:
        info["login:agy"] = (Path.home() / ".gemini" / "antigravity-cli").exists()
        if not info["login:agy"]: probs.append("agy: no CLI profile (~/.gemini/antigravity-cli); run `agy` once and sign in")
    if "gemini-api" in used: info["key:GEMINI_API_KEY"] = True
    tools = ["ffmpeg", "ffprobe"] + (["node", "npx"] if any(s in need for s in ("preview", "ship")) else [])
    for t in tools:
        info[f"bin:{t}"] = bool(shutil.which(t))
        if not info[f"bin:{t}"]: probs.append(f"{t} not on PATH")
    files = {"venv": ".venv-tts/bin/python"}
    if "audio" in need: files.update(kokoro="models/kokoro-v1.0.onnx", voices="models/voices-v1.0.bin", whisper="tools/whisper.cpp/build/bin/whisper-cli", whisper_model="tools/whisper.cpp/models/ggml-small.en.bin")
    if any(s in need for s in ("preview", "ship")): files.update(remotion="remotion/node_modules/.bin/remotion")
    for k, f in files.items():
        info[f"file:{k}"] = (ROOT / f).exists()
        if not info[f"file:{k}"]: probs.append(f"missing {f} ({k})")
    return dict(ok=not probs, problems=probs, checks=info, stages=need)

# ---------------------------------------------------------------- stages
def sh(cmd, **kw):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)
    if r.returncode: raise RuntimeError(f"{' '.join(map(str, cmd))[:120]} -> exit {r.returncode}: {(r.stderr or r.stdout)[-600:]}")
    return r

def is_template(script): return "replace: one-sentence hook" in script or "Mechanism, step by step" in script

def st_plan(t):
    E = ROOT / "episodes" / t["slug"]
    if not E.exists():
        hook = t.get("hook_title") or t["title"].upper()
        sh(["bash", "scripts/new-episode.sh", t["slug"], t["id"], t.get("pillar", "sci"), hook])
    script = (E / "script.txt").read_text()
    if is_template(script):
        prompt = (ROOT / "prompts" / "writer.md").read_text().format(TITLE=t["title"], ANGLE=t["angle"], SLUG=t["slug"])
        schema = {"type": "object", "required": ["script", "brief", "claims"], "properties": {"script": {"type": "string"}, "brief": {"type": "string"},
                  "claims": {"type": "array", "items": {"type": "string"}}}}
        r = llm.run("writer", prompt, workdir=ROOT, schema=schema, read_only=True, log_dir=ROOT / "qa" / "queue" / t["slug"])
        j = r.get("json") or {}
        if not j.get("script"): raise RuntimeError(f"writer returned no script ({r.get('meta', {}).get('error')})")
        (E / "script.txt").write_text(j["script"].strip() + "\n"); (E / "brief.md").write_text(j.get("brief", "") + "\n")
        # claims to verify -> facts.json skeleton (status unverified: the facts gate blocks TTS until a human/researcher verifies)
        fj = E / "facts.json"; d = json.loads(fj.read_text()) if fj.exists() else {}
        if not d.get("facts"):
            d = dict(topic=t["title"], sources=[], facts=[dict(id=f"f-{i + 1:04d}", claim=c, status="unverified", sources=[], spoken=[]) for i, c in enumerate(j.get("claims", []))])
            fj.write_text(json.dumps(d, indent=1))
        return dict(writer=r.get("meta", {}).get("provider"), cost_usd=r.get("meta", {}).get("cost_usd"))
    return dict(skipped="script already written")

def st_hooks(t):
    E = ROOT / "episodes" / t["slug"]
    sh([PY, "scripts/hooks.py", "gen", t["slug"]])
    hj = json.loads((E / "hooks.json").read_text())
    if hj.get("chosen") is None: raise RuntimeError("no hook candidate passed the rules")
    # the chosen hook replaces the draft's first sentence ONLY while the script has never been approved
    approved = subprocess.run([PY, "scripts/gates.py", "require", t["slug"], "script", "--artifact", f"episodes/{t['slug']}/script.txt"], cwd=ROOT, capture_output=True).returncode == 0
    if not approved and (E / "script.hook.txt").exists(): sh([PY, "scripts/hooks.py", "apply", t["slug"]])
    return dict(chosen=hj["candidates"][hj["chosen"]]["line"], applied=not approved, cost_usd=hj.get("cost_usd"))

def st_script(t):
    r = subprocess.run([PY, "scripts/facts.py", "check", t["slug"]], cwd=ROOT, capture_output=True, text=True)
    if r.returncode: raise Waiting(f"facts gate: {(r.stdout + r.stderr).strip()[-300:]}")
    r = subprocess.run([PY, "scripts/gates.py", "require", t["slug"], "script", "--artifact", f"episodes/{t['slug']}/script.txt"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode: raise Waiting(f"script gate closed: approve with scripts/gates.py approve {t['slug']} script --by <name> --artifact episodes/{t['slug']}/script.txt")
    return dict(gates="open")

def st_audio(t):
    E = f"episodes/{t['slug']}"; s = t["slug"]
    sh([PY, "scripts/tts.py", "am_michael", "1.08", f"{E}/script.txt"])
    sh(["bash", "-c", f"ffmpeg -loglevel error -y -i '{E}/narration_raw.wav' -af loudnorm=I=-14:TP=-1.5:LRA=7 -ar 48000 -ac 1 '{E}/narration.wav' && ffmpeg -loglevel error -y -i '{E}/narration.wav' -ar 16000 -ac 1 '{E}/narration16k.wav'"])
    sh([PY, "scripts/captions.py", E])           # exits non-zero when script alignment breaks
    shutil.copy(ROOT / E / "captions.json", ROOT / "remotion" / "src" / f"{s}.captions.json")
    sh(["bash", "scripts/mix_one.sh", s])
    d = ROOT / "remotion/src/durations.json"; dj = json.loads(d.read_text())
    dj[s] = round(float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"remotion/public/{s}.wav"]).stdout), 6)
    d.write_text(json.dumps(dj)); return dict(duration_s=dj[s])

def _loop(t, until):
    suf = t.get("suf", "v1"); cmd = [PY, "scripts/build_loop.py", t["id"], t["slug"], suf, "--until", until]
    if t.get("prev"): cmd += ["--prev", t["prev"]]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    tail = (r.stdout or "")[-800:]
    if r.returncode: raise RuntimeError(f"build_loop {until} exit {r.returncode}: {(r.stderr or tail)[-600:]}")
    st = json.loads((ROOT / "qa" / t["id"] / suf / "loop_state.json").read_text())
    return dict(loop_step=st.get("step"), verdict=st.get("verdict"))

def st_preview(t): return _loop(t, "preview")
def st_ship(t):
    out = _loop(t, "judge")
    suf = t.get("suf", "v1")
    r = subprocess.run([PY, "scripts/publish.py", "pack", t["id"], t["slug"], "--suf", suf], cwd=ROOT, capture_output=True, text=True)
    out["publish_pack"] = "ok" if r.returncode == 0 else f"failed: {(r.stderr or r.stdout)[-200:]}"
    return out
RUN = dict(plan=st_plan, hooks=st_hooks, script=st_script, audio=st_audio, preview=st_preview, ship=st_ship)

def process(t, stop_at, retry_failed, dry):
    s = load_state(t["slug"]); s.update(title=t["title"], id=t["id"])
    if t.get("approved") is not True:
        s["status"] = "skipped"; (None if dry else save_state(s)); print(f"[{t['slug']}] skipped (approved != true)"); return s
    if s["status"] == "failed" and not retry_failed:
        print(f"[{t['slug']}] failed earlier at {s.get('failed_stage')} (use --retry-failed)"); return s
    todo = [x for x in STAGES[: STAGES.index(stop_at) + 1] if x not in s["stages_done"]]
    if dry: print(f"[{t['slug']}] would run: {todo or '(nothing: done up to ' + stop_at + ')'}"); return s
    s["status"] = "running"; s["attempts"] += 1; save_state(s)
    for stage in todo:
        t0 = time.time()
        try:
            info = RUN[stage](t)
        except Waiting as w:
            s.update(status="waiting", waiting_on=str(w), waiting_stage=stage); log(s, stage, "waiting", reason=str(w)[:300]); return s
        except Exception as e:
            s.update(status="failed", failed_stage=stage, last_error=f"{type(e).__name__}: {e}"[:1200]); log(s, stage, "failed", error=str(e)[:300], tb=traceback.format_exc()[-400:]); return s
        s["stages_done"].append(stage); s.pop("waiting_on", None); log(s, stage, "done", wall_s=round(time.time() - t0, 1), **(info or {}))
    s["status"] = "done" if stop_at == STAGES[-1] else f"stopped_at_{stop_at}"; save_state(s); return s

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch", "--batch-file", dest="batch"); ap.add_argument("--stop-at", default="ship", choices=STAGES)
    ap.add_argument("--only"); ap.add_argument("--retry-failed", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--preflight", action="store_true"); ap.add_argument("--status", action="store_true"); ap.add_argument("--skip-preflight", action="store_true")
    a = ap.parse_args()
    if a.status:
        rows = [json.loads(p.read_text()) for p in sorted(STATE_DIR.glob("*.json"))]
        for r in rows: print(f"{r['slug']:32s} {r['status']:18s} done={','.join(r['stages_done']) or '-'} {r.get('waiting_on') or r.get('last_error') or ''}"[:200])
        sys.exit(0)
    if a.preflight or not a.skip_preflight:
        pf = preflight(a.stop_at)
        print("preflight", "PASS" if pf["ok"] else "FAIL", json.dumps(pf["checks"]))
        for p in pf["problems"]: print("  -", p)
        if a.preflight: sys.exit(0 if pf["ok"] else 2)
        if not pf["ok"] and not a.dry_run: sys.exit(2)
    if not a.batch: ap.error("--batch is required (or --preflight / --status)")
    topics = [resolve(t) for t in load_topics(a.batch)]
    if a.only: topics = [t for t in topics if t["slug"] == a.only]
    summary = [process(t, a.stop_at, a.retry_failed, a.dry_run) for t in topics]
    print(json.dumps([dict(slug=s["slug"], status=s["status"], done=s["stages_done"]) for s in summary], indent=1))
