#!/usr/bin/env python3
"""Pipeline metrics.
  metrics.py run --ep <slug|all> --stage <tts|captions|mix|render|qa|...> [--iter N] [--out FILE] -- <command...>
      runs the command, records wall-clock, CPU time (user+sys of the whole process tree), peak tree RSS,
      exit code and output file size into metrics/runs.jsonl (append-only), then rebuilds metrics/metrics.json.
  metrics.py note --ep X --stage Y --key K --value V      record a manual fact (e.g. script authored by the bot)
  metrics.py summary                                      rebuild metrics/metrics.json + docs/METRICS.md
Money cost: every tool in this pipeline is local/free (Kokoro, whisper.cpp, faster-whisper, Remotion, FFmpeg,
Kenney CC0 SFX), so cost_usd is recorded as 0.0. LLM tokens used by the authoring bot are NOT visible to these scripts."""
import argparse, json, os, resource, subprocess, sys, time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "metrics" / "runs.jsonl"
PAGE = os.sysconf("SC_PAGE_SIZE")

def tree_rss(pid):
    kids = {}
    for p in os.listdir("/proc"):
        if p.isdigit():
            try:
                st = open(f"/proc/{p}/stat").read().rsplit(")", 1)[1].split()
                kids.setdefault(int(st[1]), []).append(int(p))
            except OSError:
                pass
    tot, stack = 0, [pid]
    while stack:
        q = stack.pop()
        try:
            tot += int(open(f"/proc/{q}/statm").read().split()[1]) * PAGE
        except OSError:
            pass
        stack += kids.get(q, [])
    return tot

def record(rec):
    RUNS.parent.mkdir(exist_ok=True)
    with open(RUNS, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    summary()

def run(a, cmd):
    r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.time()
    p = subprocess.Popen(cmd)
    peak = 0
    while p.poll() is None:
        peak = max(peak, tree_rss(p.pid))
        time.sleep(0.25)
    wall = time.time() - t0
    r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    out = Path(a.out) if a.out else None
    record(dict(ts=datetime.now().astimezone().isoformat(timespec="seconds"), ep=a.ep, stage=a.stage, iter=a.iter,
                cmd=" ".join(cmd)[:300], exit=p.returncode, wall_s=round(wall, 2),
                cpu_s=round((r1.ru_utime - r0.ru_utime) + (r1.ru_stime - r0.ru_stime), 2),
                peak_rss_mb=round(peak / 2**20), out=str(out) if out else None,
                out_mb=round(out.stat().st_size / 2**20, 2) if out and out.exists() else None, cost_usd=0.0))
    return p.returncode

def load():
    return [json.loads(l) for l in open(RUNS)] if RUNS.exists() else []

def summary():
    runs = load()
    eps = {}
    for r in runs:
        e = eps.setdefault(r["ep"], {"stages": {}, "qa_iterations": 0, "render_iterations": 0, "cost_usd": 0.0})
        if r["stage"] == "note":
            e.setdefault("notes", {})[r["key"]] = r["value"]; continue
        s = e["stages"].setdefault(r["stage"], {"runs": 0, "wall_s_total": 0.0, "wall_s_last": None, "cpu_s_total": 0.0, "peak_rss_mb": 0, "out_mb_last": None})
        s["runs"] += 1; s["wall_s_total"] = round(s["wall_s_total"] + r["wall_s"], 2); s["wall_s_last"] = r["wall_s"]
        s["cpu_s_total"] = round(s["cpu_s_total"] + r["cpu_s"], 2); s["peak_rss_mb"] = max(s["peak_rss_mb"], r["peak_rss_mb"])
        if r.get("out_mb") is not None: s["out_mb_last"] = r["out_mb"]
        if r["stage"] == "qa": e["qa_iterations"] = max(e["qa_iterations"], r.get("iter") or 0)
        if r["stage"] == "render": e["render_iterations"] = max(e["render_iterations"], r.get("iter") or 0)
    meta = {"generated": datetime.now().astimezone().isoformat(timespec="seconds"), "cost_usd_total": 0.0,
            "llm_tokens": "not available to the pipeline (authoring bot's token usage is not exposed)", "episodes": eps}
    (ROOT / "metrics" / "metrics.json").write_text(json.dumps(meta, indent=2))
    rows = ["| episode | stage | runs | last wall (s) | total wall (s) | CPU (s) | peak RAM (MB) | output (MB) | cost |", "|---|---|---|---|---|---|---|---|---|"]
    for ep, e in sorted(eps.items()):
        for st, s in e["stages"].items():
            rows.append(f"| {ep} | {st} | {s['runs']} | {s['wall_s_last']} | {s['wall_s_total']} | {s['cpu_s_total']} | {s['peak_rss_mb']} | {s['out_mb_last'] or '–'} | $0 |")
    it = ["", "| episode | render iterations | QA iterations |", "|---|---|---|"] + [f"| {ep} | {e['render_iterations']} | {e['qa_iterations']} |" for ep, e in sorted(eps.items()) if ep != "all"]
    tot = ["", "| episode | total machine wall time (s) | total CPU (s) | peak RAM (MB) | cost |", "|---|---|---|---|---|"]
    for ep, e in sorted(eps.items()):
        st = e["stages"].values()
        if st: tot.append(f"| {ep} | {round(sum(x['wall_s_total'] for x in st), 1)} | {round(sum(x['cpu_s_total'] for x in st), 1)} | {max(x['peak_rss_mb'] for x in st)} | $0 |")
    notes = ["", "Notes:"] + [f"- {ep} · {k}: {v}" for ep, e in sorted(eps.items()) for k, v in e.get("notes", {}).items()]
    it = it + tot + (notes if len(notes) > 2 else [])
    (ROOT / "docs" / "METRICS.md").write_text("# Generation metrics (auto-generated by scripts/metrics.py)\n\nAll tools are local and free: cost $0.00. LLM token counts are not available to the pipeline.\n\n" + "\n".join(rows + it) + "\n")

if __name__ == "__main__":
    argv = sys.argv[1:]
    cmd = argv[argv.index("--") + 1:] if "--" in argv else []
    argv = argv[:argv.index("--")] if "--" in argv else argv
    ap = argparse.ArgumentParser(); ap.add_argument("action"); ap.add_argument("--ep", default="all"); ap.add_argument("--stage", default="misc")
    ap.add_argument("--iter", type=int); ap.add_argument("--out"); ap.add_argument("--key"); ap.add_argument("--value")
    a = ap.parse_args(argv)
    if a.action == "run": sys.exit(run(a, cmd))
    if a.action == "note": record(dict(ts=datetime.now().astimezone().isoformat(timespec="seconds"), ep=a.ep, stage="note", key=a.key, value=a.value))
    if a.action == "summary": summary()
