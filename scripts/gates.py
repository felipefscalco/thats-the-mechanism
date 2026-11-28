#!/usr/bin/env python3
"""Toggleable human/auto gates + approvals log (r5; shorts-kit's storyboard/stills + fact gates, made switchable).

  gates.py require <episode> <gate> [--artifact PATH]   exit 0 if the gate is open (off / auto / human-approved for THIS artifact hash), else 2
  gates.py approve <episode> <gate> --by NAME [--changes "what changed" | --no-changes] [--artifact PATH] [--note TEXT]
  gates.py auto    <episode> <gate> --ok 0|1 [--note]   log an automated decision (called by the pipeline)
  gates.py stats                                         per-gate approvals, % without changes, current no-change streak, auto suggestions
Config: pipeline.config.json (gates.<name>.mode = human|auto|off). Log: approvals/approvals.jsonl (append-only)."""
import argparse, hashlib, json, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "pipeline.config.json").read_text())
LOG = ROOT / "approvals" / "approvals.jsonl"


def sha(p):
    p = ROOT / p if p and not Path(p).is_absolute() else Path(p) if p else None
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p and p.exists() else None


def records():
    return [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()] if LOG.exists() else []


def append(rec):
    LOG.parent.mkdir(exist_ok=True)
    rec = {"ts": datetime.now().astimezone().isoformat(timespec="seconds"), **rec}
    with LOG.open("a") as fh: fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def critic_for(artifact: str):
    """A critic JSON under qa/ that judged exactly this MP4 (same path, relative to the repo), with scores."""
    want = str((ROOT / artifact).resolve().relative_to(ROOT)) if (ROOT / artifact).resolve().is_relative_to(ROOT) else artifact
    digest = sha(artifact)
    if not digest: return None
    for p in sorted((ROOT / "qa").rglob("*.json")):
        if "critic" not in p.name and "cal" not in p.name: continue
        try: d = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError): continue
        # the SAME cut: renders are overwritten in place, so a path match alone can be an older iteration (r10: it3's critic
        # matched an it13 MP4). Critic JSONs from before mp4_sha existed never count.
        if isinstance(d, dict) and d.get("mp4") == want and d.get("mp4_sha") == digest and (d.get("scores") or d.get("overall_score") is not None):
            return str(p.relative_to(ROOT))
    return None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("episode", nargs="?"); ap.add_argument("gate", nargs="?")
    ap.add_argument("--by", default=""); ap.add_argument("--changes", default=None); ap.add_argument("--no-changes", action="store_true")
    ap.add_argument("--artifact"); ap.add_argument("--note", default=""); ap.add_argument("--ok", type=int, default=1)
    ap.add_argument("--skip-critic", default="", help="final gate only: approve without a critic report (reason is logged)")
    a = ap.parse_args()
    if a.cmd == "stats":
        by = {}
        for r in records():
            if r.get("kind") != "human": continue
            g = by.setdefault(r["gate"], dict(n=0, no_change=0, streak=0))
            g["n"] += 1; nc = not r.get("changes"); g["no_change"] += nc; g["streak"] = g["streak"] + 1 if nc else 0
        k = CFG["autonomy"]["suggest_auto_after_streak"]
        for name, g in sorted(by.items()):
            mode = CFG["gates"].get(name, {}).get("mode", "?")
            tip = " -> suggest mode=auto" if mode == "human" and g["streak"] >= k else ""
            print(f"{name:13s} mode={mode:5s} approvals={g['n']} without_changes={g['no_change']} ({100 * g['no_change'] // max(1, g['n'])}%) streak={g['streak']}/{k}{tip}")
        return 0
    gate = CFG["gates"].get(a.gate)
    if gate is None: sys.exit(f"unknown gate {a.gate}")
    if a.cmd == "approve":
        if a.changes is None and not a.no_changes: sys.exit("say --no-changes or --changes '...'")
        skip = ""
        if a.gate == "final":   # r10 (e07 test): no episode closes without feeding the improvement loop
            if not a.artifact: sys.exit("final: pass --artifact renders/<Id>_<suf>.mp4 (the exact cut being approved)")
            crit = critic_for(a.artifact)
            if not crit and not a.skip_critic:
                sys.exit(f"final: no critic report for {a.artifact}. Run the critic first, e.g.\n"
                         f"  .venv-tts/bin/python scripts/critic.py <Id> --role critic_deep --mp4 {a.artifact} --qa-report qa/<Id>/<suf>/report_itN.json "
                         f"--out-dir qa/<Id>/<suf>/critic --name critic_cal\n  then scripts/lessons.py --merge <that critic_cal.json>\n"
                         "or approve with --skip-critic \"<reason>\" (logged).")
            skip = "" if crit else a.skip_critic
            a.note = (a.note + " " if a.note else "") + (f"critic: {crit}" if crit else f"critic SKIPPED: {skip}")
        r = append(dict(kind="human", episode=a.episode, gate=a.gate, by=a.by, changes=None if a.no_changes else a.changes,
                        artifact=a.artifact, sha=sha(a.artifact), note=a.note)); print("logged", r); return 0
    if a.cmd == "auto":
        r = append(dict(kind="auto", episode=a.episode, gate=a.gate, ok=bool(a.ok), note=a.note)); print("logged", r); return 0
    if a.cmd == "require":
        import os
        mode = gate["mode"]
        ov = os.environ.get(f"GATE_MODE_{a.gate.upper()}")
        if ov and ov != mode:  # explicit, logged override (e.g. owner offline mid-run); never silent
            append(dict(kind="override", episode=a.episode, gate=a.gate, from_mode=mode, to_mode=ov, note=os.environ.get("GATE_NOTE", "")))
            print(f"gate {a.gate}: mode overridden {mode} -> {ov} (logged)"); mode = ov
        if mode == "off": print(f"gate {a.gate}: off"); return 0
        if mode == "auto": print(f"gate {a.gate}: auto (decided by its check)"); return 0
        h = sha(a.artifact) if a.artifact else None
        ok = [r for r in records() if r.get("kind") == "human" and r["gate"] == a.gate and r["episode"] in (a.episode, "*") and (h is None or r.get("sha") in (h, None))]
        if ok: print(f"gate {a.gate}: approved by {ok[-1]['by']} at {ok[-1]['ts']}"); return 0
        print(f"gate {a.gate}: BLOCKED - needs human approval of {a.artifact or gate.get('artifact')} (scripts/gates.py approve {a.episode} {a.gate} --by Felipe --no-changes|--changes ...)")
        return 2
    sys.exit(f"unknown cmd {a.cmd}")


if __name__ == "__main__":
    sys.exit(main())
