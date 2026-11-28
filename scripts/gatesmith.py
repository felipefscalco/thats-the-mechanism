#!/usr/bin/env python3
"""r10 gatesmith (pilot): turn one docs/gate_backlog.json item into a CANDIDATE gate, validated before a human promotes it.

  write     the `gatesmith` role (scripts/llm.py, claude) writes gates_candidate/<ID>.py from the rule, the critic's
            proposed check and the evidence. It may inspect the evidence render with ffmpeg / ffprobe / tesseract only;
            it can edit nothing but its own candidate file and it CANNOT run it (write-then-execute is how an agent
            escapes an allowlist, L-37).
  validate  this harness runs the candidate in a subprocess with a timeout: it must FAIL on the evidence render with an
            event inside the critic's time window, and PASS on a known-good render. Result: gates_candidate/<ID>.json.
  promote   a human reads the candidate and the validation, then wires it into scripts/qa.py by hand. Never automatic.

Candidate contract: gates_candidate/<ID>.py defines check(mp4: str) -> {"ok": bool, "events": [{"t_s": float, ...}],
"detail": {...}} using only ffmpeg/ffprobe/tesseract subprocesses and numpy/PIL; no network, writes only to a temp dir.

Usage:  scripts/gatesmith.py write    <ID> --evidence renders/X.mp4 [--window 4-5,15-16]
        scripts/gatesmith.py review   <ID> --by NAME          (after a human read the candidate; pins its sha256)
        scripts/gatesmith.py validate <ID> --evidence renders/X.mp4 --window 4-5,15-16 --good renders/Y.mp4"""
import argparse, json, subprocess, sys, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import llm

CAND = ROOT / "gates_candidate"
# inspect only, through one fixed helper (no free ffmpeg/tesseract command line, no chosen output paths); never run python
TOOLS = ["Read", "Glob", "Grep", "Bash(.venv-tts/bin/python scripts/gatesmith_probe.py:*)"]
# validation runs LLM-written code: macOS sandbox, no network, writes only to the temp dirs (verified r10)
SANDBOX = '(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath "/private/var/folders") (subpath "/private/tmp") (literal "/dev/null"))'


def item(gid: str) -> dict:
    items = json.loads((ROOT / "docs" / "gate_backlog.json").read_text())["items"]
    hit = [i for i in items if i["id"] == gid]
    if not hit:
        sys.exit(f"{gid} is not in docs/gate_backlog.json")
    return hit[0]


def windows(spec: str) -> list[tuple[float, float]]:
    return [tuple(float(x) for x in w.split("-")) for w in spec.split(",") if w]


def write(a) -> int:
    it = item(a.id); CAND.mkdir(exist_ok=True)
    ev = "\n".join(f"- {e['episode']} {e['timestamp']} ({e['severity']})" for e in it["evidence"])
    task = textwrap.dedent(f"""\
        You are the GATESMITH for the "That's the Mechanism" Shorts pipeline in {ROOT}.
        Write ONE automated QA check as gates_candidate/{a.id}.py. You may only edit that file.
        Read AGENTS.md ("Enforcement hierarchy: code over prose") and two existing checks for style, e.g. scripts/framing.py
        and scripts/label_sync.py. Inspect the evidence render ONLY with
          .venv-tts/bin/python scripts/gatesmith_probe.py info|frames|ocr ...   (see its docstring)
        to design the measurement. You cannot run anything else; after a human review, a sandboxed harness runs your check.

        Contract: define check(mp4: str) -> dict(ok=bool, events=[dict(t_s=float, ...)], detail=dict). Use only subprocess
        calls to ffmpeg/ffprobe/tesseract plus numpy/PIL; work in a tempfile.TemporaryDirectory(); no network; deterministic;
        < 2 minutes on a 47 s 1080x1920 render. A failing check returns ok=False and one event per violation with its time.
        Add `if __name__ == "__main__":` that prints json.dumps(check(sys.argv[1])). Keep it short and well commented.

        It must FAIL on the evidence render {a.evidence} (violations around {a.window or 'the evidence times below'}) and
        PASS on a render where the rule holds. Do not special-case these files or times.
        """) + llm.untrusted("gate_backlog_item", json.dumps(dict(rule=it["rule"], category=it["category"],
                                                                     proposed_gate=it["proposed_gate"], kind=it["kind"]), indent=1) + "\nevidence:\n" + ev)
    spec = dict(llm.role_spec("builder"), tools=TOOLS)
    res = llm.run("gatesmith", task, ROOT, scope=[f"gates_candidate/{a.id}.py"], spec=spec, log_dir=CAND / "logs")
    out = CAND / f"{a.id}.py"
    print(json.dumps(dict(ok=res["ok"], wrote=out.exists(), meta={k: res["meta"].get(k) for k in ("provider", "model", "wall_s", "reverted", "error")}), indent=1))
    return 0 if res["ok"] and out.exists() else 1


def sha(p: Path) -> str:
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest()


def review(a) -> int:
    """A human read gates_candidate/<ID>.py: record its sha256. validate refuses any other version of the file."""
    f = CAND / f"{a.id}.py"
    if not f.exists(): sys.exit(f"{f} does not exist")
    if not a.by: sys.exit("say who reviewed it: --by NAME")
    rec = dict(sha256=sha(f), by=a.by, file=str(f.relative_to(ROOT)))
    (CAND / f"{a.id}.reviewed").write_text(json.dumps(rec, indent=1)); print("reviewed", rec); return 0


def run_candidate(gid: str, mp4: str, timeout: int = 300) -> dict:
    code = f"import json, sys; sys.path.insert(0, {str(CAND)!r}); import importlib; m = importlib.import_module({gid!r}); print(json.dumps(m.check({mp4!r})))"
    r = subprocess.run(["sandbox-exec", "-p", SANDBOX, sys.executable, "-I", "-c", code], cwd=str(ROOT), capture_output=True,
                       text=True, timeout=timeout, env=llm.child_env("agy"))
    if r.returncode:
        return dict(error=(r.stderr or r.stdout)[-800:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def validate(a) -> int:
    f, rv = CAND / f"{a.id}.py", CAND / f"{a.id}.reviewed"
    if not rv.exists() or json.loads(rv.read_text()).get("sha256") != sha(f):
        sys.exit(f"{f.name} has not been reviewed in this exact version. Read it, then: scripts/gatesmith.py review {a.id} --by NAME")
    win = windows(a.window)
    bad, good = run_candidate(a.id, str(ROOT / a.evidence)), run_candidate(a.id, str(ROOT / a.good))
    hits = [e for e in bad.get("events", []) if any(lo - 0.5 <= e.get("t_s", -9) <= hi + 0.5 for lo, hi in win)]
    verdict = dict(
        id=a.id, evidence=a.evidence, window=win, good=a.good,
        fails_on_evidence=bad.get("ok") is False and bool(hits), evidence_events=bad.get("events", [])[:12], evidence_error=bad.get("error"),
        passes_on_good=good.get("ok") is True, good_events=good.get("events", [])[:12], good_error=good.get("error"))
    verdict["promotable"] = verdict["fails_on_evidence"] and verdict["passes_on_good"]
    (CAND / f"{a.id}.json").write_text(json.dumps(verdict, indent=1))
    print(json.dumps({k: verdict[k] for k in ("fails_on_evidence", "passes_on_good", "promotable", "evidence_error", "good_error")}),
          f"\nevidence events in window: {len(hits)}/{len(bad.get('events', []))}; good events: {len(good.get('events', []))}")
    return 0 if verdict["promotable"] else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["write", "review", "validate"]); ap.add_argument("id")
    ap.add_argument("--evidence", default=""); ap.add_argument("--window", default=""); ap.add_argument("--good", default="")
    ap.add_argument("--by", default="")
    a = ap.parse_args()
    sys.exit(write(a) if a.cmd == "write" else review(a) if a.cmd == "review" else validate(a))
