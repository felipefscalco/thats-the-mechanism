"""r10 improvement-loop tests: critic output must turn into work, not stay in a report.
  - polish.select: blocker/major weaknesses only, flagged when a gate measured the same thing as OK
  - lessons.gate_misses: a rule the critic reports on a render whose matching gate PASSED is a gate miss
  - lessons.render_prompt: active candidate gates and gate misses reach the builder as interim rules
  - lessons.write_backlog: gate misses first, with the evidence a new gate must fail on
Run: .venv-tts/bin/python tests/test_r10_learning.py"""
import json, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import lessons, polish

CLEAR = next(w for _, w in lessons.KNOWN_GATES if "icon/label clearance" in w)
HOLD = next(w for _, w in lessons.KNOWN_GATES if "no stage hold" in w)


def _report(tmp: Path, ok_clear: bool, ok_hold: bool) -> str:
    p = ROOT / "_scratch" / f"t_r10_report_{tmp.name}_{int(ok_clear)}{int(ok_hold)}.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(dict(checks=[dict(check="labels: icon/label clearance >= 36 px (held >= 0.6 s)", ok=ok_clear, detail={}),
                                         dict(check="motion: no stage hold > 2.0 s", ok=ok_hold, detail={})])))
    return str(p.relative_to(ROOT))


def t_polish_select():
    cal = dict(verdict="ONE MORE PASS", weaknesses=[
        dict(timestamp="0:01", severity="minor", category="design", issue="tiny kerning", fix="x"),
        dict(timestamp="0:17", severity="major", category="motion_craft", issue="3 s of near-static hold on the cutaway", fix="push in"),
        dict(timestamp="0:04", severity="blocker", category="voice_captions", issue="caption words fuse", fix="gap"),
    ])
    rep = dict(checks=[dict(check="motion: no stage hold > 2.0 s", ok=True)])
    items = polish.select(cal, rep)
    assert [x["timestamp"] for x in items] == ["0:04", "0:17"], items          # minor dropped, blocker first
    assert items[1]["measured_ok"] == ["motion: no stage hold > 2.0 s"], items  # gate says OK -> confirm on stills
    txt = polish.task_text(items)
    assert txt.startswith('<untrusted_data source="critic_weaknesses">') and "Confirm it on the stills" in txt


def t_gate_miss():
    tmp = Path(tempfile.mkdtemp())
    member = dict(episode="X", evidence="0:38", source="qa/X/critic_cal.json")
    passed = [dict(member, qa_report=_report(tmp, True, True))]
    failed = [dict(member, qa_report=_report(tmp, False, True))]
    m = lessons.gate_misses([CLEAR], passed)
    assert len(m) == 1 and m[0]["check"].startswith("labels: icon/label clearance") and m[0]["timestamp"] == "0:38", m
    assert lessons.gate_misses([CLEAR], failed) == []          # the gate caught it: not a miss
    assert lessons.gate_misses([CLEAR], [member]) == []        # no QA report recorded: cannot judge


def _cluster(rule, enforcement, active=True, miss=None, sev="major"):
    return dict(id="R-1", rule=rule, category="c", enforcement=enforcement, active=active, severity=sev, measurable=True,
                proposed_gate="g", gates=[], components=[], episodes=["X"], episode_count=1,
                evidence=[dict(episode="X", timestamp="0:01", severity=sev, source="s")], gate_miss=miss or [])


def t_interim_rules_in_prompt():
    clusters = [_cluster("Keep the hero moving.", "prose"), _cluster("Never strand a word on a caption line.", "candidate_gate"),
                _cluster("Labels never collide.", "gate", miss=[dict(episode="X", timestamp="0:38", check="labels: icon/label clearance")]),
                _cluster("Inactive candidate.", "candidate_gate", active=False)]
    p = lessons.render_prompt(clusters)
    assert "1. Keep the hero moving." in p
    assert "Never strand a word" in p and "gate not written yet" in p
    assert "Labels never collide." in p and "a gate exists but missed it" in p
    assert "Inactive candidate." not in p


def t_backlog_order_and_evidence():
    out = Path(tempfile.mkdtemp()) / "gate_backlog.json"
    saved, lessons.OUT_BACKLOG = lessons.OUT_BACKLOG, out
    try:
        lessons.write_backlog([_cluster("cand minor", "candidate_gate", sev="minor"), _cluster("prose only", "prose"),
                               _cluster("missed", "gate", miss=[dict(episode="X", timestamp="0:38", check="c")]),
                               _cluster("cand blocker", "candidate_gate", sev="blocker")])
    finally:
        lessons.OUT_BACKLOG = saved
    items = json.loads(out.read_text())["items"]
    assert [i["rule"] for i in items] == ["missed", "cand blocker", "cand minor"], items   # misses first, then by severity
    assert all(i["evidence"] for i in items) and items[0]["kind"] == "gate_miss"


def _simulate(polish_wins: bool):
    """Run scripts/build_loop.py end to end with every render, QA, critic and LLM call faked: checks the state machine
    (preview -> ship -> judge -> polish -> preview -> ship -> judge) and that a losing polish is reverted."""
    import runpy, subprocess, types
    import llm as llm_mod
    cid, suf, slug = "ZzLoopTest", "t", "99-zz"
    qa = ROOT / "qa" / cid / suf; tsx = ROOT / "remotion" / "src" / "episodes" / f"{cid}.tsx"
    mp4 = ROOT / "renders" / f"{cid}_{suf}.mp4"; prev = ROOT / "_scratch" / "zz_prev.mp4"
    qa.mkdir(parents=True, exist_ok=True); tsx.write_text("// v1 accepted\n"); mp4.write_bytes(b"render-v1"); prev.write_bytes(b"prev")
    (qa / "loop_state.json").write_text(json.dumps(dict(step="preview", it=1, ship_it=0, events=[])))
    calls = dict(ship_check=0)

    def fake_run(cmd, **kw):
        s = " ".join(map(str, cmd))
        if "preview.py" in s:
            n = cmd[-1]; (qa / f"preview_it{n}.json").write_text(json.dumps(dict(checks=[dict(check="x", ok=True)])))
        elif "iterate.sh" in s:
            n = cmd[2]; mp4.write_bytes(b"render-" + tsx.read_text().encode())
            (qa / f"report_it{n}.json").write_text(json.dumps(dict(checks=[dict(check="motion: no stage hold > 2.0 s", ok=True)])))
        elif "ship_check.sh" in s:
            calls["ship_check"] += 1; out = Path(cmd[-2] if len(cmd) > 7 else cmd[-1]); out.mkdir(parents=True, exist_ok=True)
            first = calls["ship_check"] == 1
            (out / "ship.json").write_text(json.dumps(dict(ship=True if first else polish_wins, decided_by="pairwise")))
            (out / "critic_cal.json").write_text(json.dumps(dict(verdict="ONE MORE PASS", weaknesses=[
                dict(timestamp="0:10", severity="major", category="clarity", issue="scale proof unclear", fix="hold it longer")])))
        return subprocess.CompletedProcess(cmd, 0, "", "")

    def fake_llm(role, prompt, *a, **k):
        if role == "builder" and "polish round" in prompt:
            assert "<untrusted_data" in prompt and "scale proof unclear" in prompt
            tsx.write_text("// v2 polished\n")
        return dict(ok=True, text="FIXED", json=None, meta=dict(provider="fake"))

    real_run, real_llm, argv = subprocess.run, llm_mod.run, sys.argv
    subprocess.run, llm_mod.run = fake_run, fake_llm
    sys.argv = ["build_loop.py", cid, slug, suf, "--prev", str(prev)]
    try:
        runpy.run_path(str(ROOT / "scripts" / "build_loop.py"), run_name="__main__")
        st = json.loads((qa / "loop_state.json").read_text())
        return st, tsx.read_text(), mp4.read_bytes(), calls
    finally:
        subprocess.run, llm_mod.run, sys.argv = real_run, real_llm, argv
        import shutil
        shutil.rmtree(ROOT / "qa" / cid, ignore_errors=True); tsx.unlink(missing_ok=True); prev.unlink(missing_ok=True)
        for f in (ROOT / "renders").glob(f"{cid}_*"): f.unlink()


def t_build_loop_polish_reverts_a_loser():
    st, tsx, mp4, calls = _simulate(polish_wins=False)
    kinds = [e["kind"] for e in st["events"]]
    assert calls["ship_check"] == 2 and "polish_builder" in kinds and "polish_reverted" in kinds, kinds
    assert st["step"] == "done" and tsx == "// v1 accepted\n" and mp4 == b"render-// v1 accepted\n", (tsx, mp4)   # accepted render restored
    assert st["verdict"]["ship"] is True and st["ship_report"].endswith("polish1_base_report.json")


def t_build_loop_polish_keeps_a_winner():
    st, tsx, mp4, calls = _simulate(polish_wins=True)
    kinds = [e["kind"] for e in st["events"]]
    assert calls["ship_check"] == 2 and "polish_reverted" not in kinds and kinds[-1] == "polish_stop", kinds   # max 1 round
    assert tsx == "// v2 polished\n" and mp4 == b"render-// v2 polished\n", (tsx, mp4)
    assert any(e["kind"] == "ship_render_qa" for e in st["events"]) and Path(st["ship_report"]).name == "report_it111.json"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("t_"):
            fn(); print("PASS", name)
    for f in (ROOT / "_scratch").glob("t_r10_report_*.json"):
        f.unlink()
