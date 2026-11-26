#!/usr/bin/env python3
"""r7 preview-first build loop (vendor-neutral; every LLM call goes through scripts/llm.py roles).

  plan      planner role writes the frozen plan episodes/<slug>/VIDEO.md (separate session; builder only gets VIDEO.md)
  build     builder role implements VIDEO.md, checks key stills (hook / mid / end) first      [fresh session]
  preview   scripts/preview.py: all still-measurable gates, no full render
  route     failing checks -> fixer role if they are ALL value fixes (contrast / edge / overlap / font size), else builder
            fixer edits are diffed by scripts/fixer_guard.py and reverted when they leave the allowlist (then builder)
  critique  builder self-reviews the preview contact sheet + key stills before any critic sees the video
  ship      ONE full render + master + qa.py (all gates incl. audio); failures route back (max_ship_iters)
  judge     scripts/ship_check.sh (critic roles; tie-breaker) vs the previous render
State is saved after every step in qa/<Id>/<SUF>/loop_state.json, so a rerun resumes where it stopped.
Usage: build_loop.py <CompId> <slug> <SUF> --prev renders/X.mp4 [--prev-qa report.json] [--task-file F] [--replan] [--until preview|ship|judge]
"""
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import llm, fixer_guard

ROOT = llm.ROOT
PY = str(ROOT / ".venv-tts/bin/python") if (ROOT / ".venv-tts/bin/python").exists() else sys.executable
ap = argparse.ArgumentParser(); ap.add_argument("id"); ap.add_argument("slug"); ap.add_argument("suf")
ap.add_argument("--prev"); ap.add_argument("--prev-qa"); ap.add_argument("--task-file"); ap.add_argument("--plan-extra-file")
ap.add_argument("--replan", action="store_true"); ap.add_argument("--until", default="judge", choices=["plan", "preview", "ship", "judge"])
A = ap.parse_args()
CFG = llm.config().get("loop", {})
MAXP, MAXS = int(CFG.get("max_preview_iters", 4)), int(CFG.get("max_ship_iters", 2))
FIXER_CHECKS = CFG.get("fixer_checks", ["labels: WCAG", "labels: inside Shorts UI safe zones", "labels: icon/label clearance", "labels: minimum font size", "text: no raw SVG/CSS fontSize"])
QA = ROOT / "qa" / A.id / A.suf; QA.mkdir(parents=True, exist_ok=True); LOGS = QA / "llm"
TSX = f"remotion/src/episodes/{A.id}.tsx"; VIDEO = ROOT / "episodes" / A.slug / "VIDEO.md"
STATE = QA / "loop_state.json"
st = json.loads(STATE.read_text()) if STATE.exists() else dict(step="plan", it=0, ship_it=0, events=[])
def save(): STATE.write_text(json.dumps(st, indent=1))
def ev(kind, **kw):
    st["events"].append(dict(t=time.strftime("%H:%M:%S"), kind=kind, **kw)); save(); print(f"[loop {A.id}] {kind} {json.dumps(kw)[:300]}", flush=True)
def fill(tpl, **kw):
    for k, v in kw.items(): tpl = tpl.replace("{" + k + "}", str(v))
    return tpl
def prompt(name, **kw): return fill((ROOT / "prompts" / f"{name}.md").read_text(), ROOT=ROOT, ID=A.id, SLUG=A.slug, SUF=A.suf, **kw)
SCOPE = [TSX, f"episodes/{A.slug}/*.json", f"episodes/{A.slug}/notes*.md", f"episodes/{A.slug}/shots.md"]   # VIDEO.md is NOT in scope: the plan is frozen

def sh(cmd, env=None):
    t = time.time(); r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env={**os.environ, **(env or {})})
    return r, round(time.time() - t, 1)

def preview(n):
    r, w = sh([PY, "scripts/preview.py", A.id, A.slug, str(n)], env=dict(SUF=A.suf))
    rep = json.loads((QA / f"preview_it{n}.json").read_text()) if (QA / f"preview_it{n}.json").exists() else dict(checks=[dict(check="preview ran", ok=False, detail=r.stderr[-800:])])
    fails = [c for c in rep["checks"] if not c["ok"]]
    ev("preview", it=n, wall_s=w, failed=[c["check"] for c in fails]); return fails

def fmt(fails): return "\n".join(f"- {c['check']}: {json.dumps(c['detail'])[:900]}" for c in fails)

def run_builder(task, n):
    res = llm.run("builder", prompt("builder", TASK=task, MAX_TRIES=2), ROOT, scope=SCOPE, log_dir=LOGS)
    ev("builder", it=n, ok=res["ok"], **{k: res["meta"].get(k) for k in ("provider", "model", "wall_s", "cost_usd", "reverted", "error")})
    return res

def run_fixer(fails, n):
    before = (ROOT / TSX).read_text()
    res = llm.run("fixer", prompt("fixer", FAILS=fmt(fails)), ROOT, scope=[TSX], log_dir=LOGS)
    after = (ROOT / TSX).read_text()
    g = fixer_guard.check(before, after)
    tsc, _ = sh(["bash", "-c", "cd remotion && npx tsc --noEmit -p ."])
    ok = res["ok"] and g["ok"] and tsc.returncode == 0 and after != before
    if not ok:
        (ROOT / TSX).write_text(before)   # guard: revert the whole fixer edit
    ev("fixer", it=n, ok=ok, guard_ok=g["ok"], violations=g["violations"][:4], tsc_ok=tsc.returncode == 0, unchanged=after == before,
       **{k: res["meta"].get(k) for k in ("provider", "model", "wall_s", "cost_usd", "error")})
    return ok

def route(fails, n, stage):
    value_only = all(any(c["check"].startswith(p) for p in FIXER_CHECKS) for c in fails)
    if value_only and run_fixer(fails, n):
        return "fixer"
    run_builder(f"The {stage} gates failed. Fix the root cause in the composition (structure is yours to change, but follow VIDEO.md).\n"
                f"Failing checks:\n{fmt(fails)}\nPreview contact sheet: {QA}/preview_sheet_it{n}.png (open it).", n)
    return "builder"

# ---- plan ----
if st["step"] == "plan":
    if A.replan or not VIDEO.exists():
        extra = Path(A.plan_extra_file).read_text() if A.plan_extra_file else ""
        res = llm.run("planner", prompt("planner", EXTRA=extra), ROOT, read_only=True, log_dir=LOGS)
        ev("planner", ok=res["ok"], **{k: res["meta"].get(k) for k in ("provider", "model", "wall_s", "cost_usd", "error")})
        if not res["ok"] or "## Shots" not in res["text"]: sys.exit("planner failed")
        VIDEO.write_text(res["text"].strip() + "\n")
    st["step"] = "build"; save()
if A.until == "plan": sys.exit(0)
# ---- build (fresh session, key stills first) ----
if st["step"] == "build":
    task = Path(A.task_file).read_text() if A.task_file else "Implement VIDEO.md in the composition. Start with the three key stills (hook / mid / end) and confirm them before the rest."
    run_builder(task, 0); st.update(step="preview", it=1); save()
# ---- preview loop ----
while st["step"] == "preview":
    fails = preview(st["it"])
    if not fails:
        st["step"] = "critique"; save(); break
    if st["it"] >= MAXP:
        ev("preview_cap", it=st["it"]); st["step"] = "critique"; save(); break
    st["last_route"] = route(fails, st["it"], "preview"); st["it"] += 1; save()
# ---- self-critique ----
if st["step"] == "critique":
    n = st["it"]; before = (ROOT / TSX).read_text()
    res = llm.run("builder", prompt("selfcritique", SHEET=QA / f"preview_sheet_it{n}.png", KEYS=QA / f"keystills_it{n}.png", N=n + 1),
                  ROOT, scope=SCOPE, log_dir=LOGS, files=[("contact sheet", QA / f"preview_sheet_it{n}.png"), ("key stills", QA / f"keystills_it{n}.png")])
    changed = (ROOT / TSX).read_text() != before
    ev("selfcritique", ok=res["ok"], changed=changed, reply=(res["text"] or "")[-600:], **{k: res["meta"].get(k) for k in ("provider", "wall_s", "cost_usd")})
    if changed:
        st["it"] = n + 1; fails = preview(st["it"])
        if fails: ev("selfcritique_regressed", failed=[c["check"] for c in fails])
    st["step"] = "ship"; save()
if A.until == "preview": sys.exit(0)
# ---- ship: one full render + master + all gates ----
while st["step"] == "ship":
    st["ship_it"] += 1; k = st["ship_it"]; save()
    r, w = sh(["bash", "scripts/iterate.sh", str(100 + k), A.id], env=dict(SUF=A.suf, MASTER="1"))
    rep = QA / f"report_it{100 + k}.json"
    fails = [c for c in json.loads(rep.read_text())["checks"] if not c["ok"]] if rep.exists() else [dict(check="render", detail=r.stderr[-600:])]
    ev("ship_render_qa", ship_it=k, wall_s=w, failed=[c["check"] for c in fails])
    if not rep.exists():   # infrastructure failure (render/master/QA crashed): not the builder's job, stop and keep state
        st["ship_it"] -= 1; save(); sys.exit(f"ship render/QA infrastructure failure, see {QA}; stderr tail: {r.stderr[-600:]}")
    if not fails:
        st.update(step="judge", ship_report=str(rep)); save(); break
    if k >= MAXS:
        st.update(step="judge", ship_report=str(rep), ship_gates_failed=[c["check"] for c in fails]); save(); break
    route(fails, k, "full-render"); pf = preview(st["it"] + 1); st["it"] += 1; save()
if A.until == "ship": sys.exit(0)
# ---- judge ----
if st["step"] == "judge" and A.prev:
    out = QA / "ship"
    r, w = sh(["bash", "scripts/ship_check.sh", A.id, str(ROOT / "renders" / f"{A.id}_{A.suf}.mp4"), A.prev, st["ship_report"], str(out)] + ([A.prev_qa] if A.prev_qa else []))
    verdict = json.loads((out / "ship.json").read_text()) if (out / "ship.json").exists() else dict(error=r.stderr[-500:])
    ev("judge", wall_s=w, ship=verdict.get("ship"), decided_by=verdict.get("decided_by"), calibrated=verdict.get("calibrated"))
    st["step"] = "done"; st["verdict"] = verdict; save()
print(json.dumps(dict(step=st["step"], verdict=st.get("verdict")), indent=1))
