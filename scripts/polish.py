#!/usr/bin/env python3
"""r10 improvement loop, episode level: turn the calibrated critic's weaknesses into the builder's next task.

build_loop.py calls this after a SHIP verdict whose calibrated verdict is still "ONE MORE PASS". Only blocker/major
weaknesses are kept. A weakness whose text matches a gate that PASSED on the same render is kept but flagged: it is
either a gate miss (real problem, gate too weak) or a critic hallucination (L-23), so the builder must confirm it on
the stills before changing anything. The result is wrapped as untrusted data (it is model output).
Usage (debug): scripts/polish.py <critic_cal.json> <report_itN.json>"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm
from lessons import KNOWN_GATES, check_for

KEEP = ("blocker", "major")


def select(cal: dict, report: dict | None, limit: int = 6) -> list[dict]:
    checks = (report or {}).get("checks", [])
    out = []
    for w in cal.get("weaknesses", []):
        if w.get("severity") not in KEEP:
            continue
        text = f"{w.get('category', '')} {w.get('issue', '')}"
        passed = []
        for pat, where in KNOWN_GATES:
            if re.search(pat, text, re.I):
                pref = check_for(where)
                hit = next((c for c in checks if pref and c["check"].startswith(pref)), None)
                if hit and hit["ok"]:
                    passed.append(hit["check"])
        out.append(dict(timestamp=w.get("timestamp", ""), severity=w["severity"], category=w.get("category", ""),
                        issue=w.get("issue", ""), fix=w.get("fix", ""), measured_ok=sorted(set(passed))))
    out.sort(key=lambda x: (x["severity"] != "blocker", bool(x["measured_ok"])))
    return out[:limit]


def task_text(items: list[dict]) -> str:
    lines = []
    for i, x in enumerate(items, 1):
        note = (f" [a gate measured this as OK: {'; '.join(x['measured_ok'])}. Confirm it on the stills first; if it is not "
                "visible there, skip it]") if x["measured_ok"] else ""
        lines.append(f"{i}. [{x['timestamp']}] ({x['severity']} · {x['category']}) {x['issue']}\n   suggested fix: {x['fix']}{note}")
    return llm.untrusted("critic_weaknesses", "\n".join(lines))


if __name__ == "__main__":
    cal = json.loads(Path(sys.argv[1]).read_text())
    rep = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 and Path(sys.argv[2]).exists() else None
    print(task_text(select(cal, rep)))
