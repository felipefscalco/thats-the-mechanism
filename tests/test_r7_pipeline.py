#!/usr/bin/env python3
"""r7 unit tests: LLM adapter argv per provider (dry-run, no CLI needed), scope guard, fixer allowlist guard.
Run: python3 tests/test_r7_pipeline.py"""
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "scripts"))
import llm, fixer_guard

def t_argv():
    wd = ROOT; sch = Path(tempfile.mkdtemp()) / "s.json"; sch.write_text('{"type":"object"}')
    files = [("VIDEO", ROOT / "README.md")]
    c, _, _ = llm.build_cmd("claude", "sonnet", "hi", wd, sch, files, read_only=True)
    assert c[:4] == ["claude", "-p", "--output-format", "json"] and "--json-schema" in c and "--allowedTools=Read,Glob,Grep" in c and "hi" not in c
    c, _, _ = llm.build_cmd("claude", None, "hi", wd, None, [], read_only=False)
    assert "--dangerously-skip-permissions" not in c and c[c.index("--permission-mode") + 1] == "default"   # r10: allowlist, no bypass
    c, _, p = llm.build_cmd("agy", "gemini-3.8-flash-high", "hi", wd, sch, files, read_only=True)   # r10: agy is read-only
    assert c[0] == "agy" and c[c.index("--model") + 1] == "gemini-3.8-flash-high" and c[-2] == "-p" and "--json-schema" in c and str(files[0][1]) in p
    c, _, _ = llm.build_cmd("codex", "gpt-5.6", "hi", wd, sch, [("IMG", ROOT / "contact_sheet.png")], read_only=True, last_msg=Path("/x/last.txt"))
    assert c[:2] == ["codex", "exec"] and c[c.index("--sandbox") + 1] == "read-only" and c[c.index("-m") + 1] == "gpt-5.6"
    assert "--output-schema" in c and c[c.index("-o") + 1] == "/x/last.txt" and "-i" in c and c[-1].endswith("hi")
    try:   # r10: codex has no path-scoped edits -> write roles refused
        llm.build_cmd("codex", None, "hi", wd, None, [], read_only=False); raise AssertionError("codex write must be refused")
    except llm.ProviderUnavailable:
        pass
    c, _, p = llm.build_cmd("cursor-agent", "sonnet-5.5", "hi", wd, sch, [], read_only=True)
    assert c[:4] == ["cursor-agent", "-p", "--output-format", "json"] and "--mode" in c and "ask" in c and "JSON Schema" in p
    try:   # r10: cursor-agent has no tool allowlist, so write roles are refused instead of run with --force
        llm.build_cmd("cursor-agent", None, "hi", wd, None, [], read_only=False); raise AssertionError("cursor-agent write must be refused")
    except llm.ProviderUnavailable:
        pass
    # role override + dry run (works even when the CLI is not installed)
    import os
    os.environ["LLM_PLANNER"] = "codex:gpt-5.6"; r = llm.run("planner", "x", read_only=True, dry_run=True); del os.environ["LLM_PLANNER"]
    assert r["meta"]["provider"] == "codex" and r["meta"]["cmd"][:2] == ["codex", "exec"]   # override honoured (read-only role)
    os.environ["LLM_BUILDER"] = "codex:gpt-5.6"; r = llm.run("builder", "x", dry_run=True); del os.environ["LLM_BUILDER"]
    assert r["meta"].get("provider") != "codex"   # r10: codex cannot take a write role
    os.environ["LLM_FIXER"] = "cursor-agent:sonnet-5.5"; r = llm.run("fixer", "x", dry_run=True); del os.environ["LLM_FIXER"]
    assert r["meta"].get("provider") != "cursor-agent"   # r10: refused for a write role, falls back (or fails) instead
    assert llm._extract_json('noise ```json\n{"a": 1}\n``` tail') == {"a": 1}
    out = llm.parse_output("cursor-agent", json.dumps({"type": "result", "is_error": False, "result": 'ok {"b":2}'}), {"type": "object"})
    assert out["json"] == {"b": 2}

def t_scope():
    d = Path(tempfile.mkdtemp())
    sh = lambda *a: subprocess.run(a, cwd=d, capture_output=True, check=True)
    sh("git", "init", "-q"); (d / "a.txt").write_text("a"); (d / "b.txt").write_text("b"); sh("git", "add", "."); sh("git", "-c", "user.email=x@y", "-c", "user.name=x", "commit", "-qm", "i")
    (d / "b.txt").write_text("b-dirty-before")
    snap = llm.snapshot(d)
    (d / "a.txt").write_text("a2"); (d / "b.txt").write_text("b2"); (d / "new.txt").write_text("n"); (d / "ok").mkdir(); (d / "ok/x.txt").write_text("x")
    rev = llm.enforce_scope(d, snap, ["ok/*"])
    assert (d / "a.txt").read_text() == "a" and (d / "b.txt").read_text() == "b-dirty-before" and not (d / "new.txt").exists() and (d / "ok/x.txt").exists(), rev
    assert set(rev) == {"a.txt", "b.txt", "new.txt"}, rev
    snap = llm.snapshot(d); (d / ".remotion").mkdir(); (d / ".remotion/chrome").write_text("bin"); (d / "metrics").mkdir(); (d / "metrics/runs.jsonl").write_text("{}")
    assert llm.enforce_scope(d, snap, ["ok/*"]) == [] and (d / ".remotion/chrome").exists()   # caches / pipeline outputs are never reverted

def t_guard():
    base = 'const A = () => <Stage><Label x={100} y={400} text="CAR" size={30} color={C.paper} />\n<g transform={`translate(${cam.x} 0) scale(${zoom})`}><rect x={80} width={920} fill="#0D0E12" /></g></Stage>;\nconst t = ease(f, 10, 20, 0, 1, EASE.OUT);'
    ok = lambda s: fixer_guard.check(base, s)["ok"]
    assert ok(base.replace("size={30}", "size={36}"))                       # font size
    assert ok(base.replace('text="CAR"', 'text="CABIN"'))                   # copy
    assert ok(base.replace("x={100}", "x={140}"))                          # edge margin / clearance
    assert ok(base.replace("C.paper", "C.amber"))                          # palette token swap
    assert ok(base.replace("EASE.OUT", "EASE.OVERSHOOT"))                   # easing
    assert ok(base.replace("10, 20", "12, 26"))                            # timing
    assert ok(base.replace("<Label x", "<TagLabel x"))                     # backing for contrast
    assert ok(base.replace(' size={30}', ' size={30} weight={700}'))       # value prop insert
    assert not ok(base.replace("scale(${zoom})", "scale(${zoom * 1.2})"))   # camera
    assert not ok(base.replace("</Stage>", "<Pill x={1} y={2} w={3} text=\"NEW\" color={C.red} s={1} /></Stage>"))  # new element
    assert not ok(base.replace('fill="#0D0E12"', 'fill="#123456"'))         # new colour
    assert not ok(base.replace("ease(f,", "spring(f,"))                     # logic
    assert not ok(base.replace("<g transform", "<g opacity={0.5} transform").replace("<rect x={80}", "<circle cx={80}"))

if __name__ == "__main__":
    for t in (t_argv, t_scope, t_guard):
        t(); print("PASS", t.__name__)
