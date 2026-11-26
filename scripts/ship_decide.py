#!/usr/bin/env python3
"""r7 ship decision with a tie-breaker (r6 gap 5: Sky v6 vs v5 tied in both orders, margin 0.0, twice).

Inputs (ship dir): cmp_prev_vs_new.json, cmp_new_vs_prev_swap.json, optional cmp_tiebreak.json (critic_tiebreak role,
a different model), optional critic_cal.json; --new-qa / --prev-qa reports (qa.py on each MP4).
Rule:
  1. Pairwise (critic role, both orders): SHIP if new preferred in >= 1 order and never loses (r6 rule).
  2. If undecided (tie/tie or split), the tie-break critic (second model) decides when it has a preference.
  3. If still tied: per-gate deltas on MP4-measurable gates both renders were checked with. SHIP only if the new
     render passes every gate the previous one passes and at least one more (strict improvement), else NO-SHIP.
Usage: ship_decide.py <ship-dir> [--new-qa report.json] [--prev-qa report.json]  -> ship-dir/ship.json
"""
import json, sys
from pathlib import Path
o = Path(sys.argv[1]); arg = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
ld = lambda n: json.loads((o / n).read_text()) if (o / n).exists() else None
a, b, tb, cal = ld("cmp_prev_vs_new.json"), ld("cmp_new_vs_prev_swap.json"), ld("cmp_tiebreak.json"), ld("critic_cal.json") or {}
side = lambda d, new_is: None if d is None else ("new" if d.get("preferred") == new_is else "tie" if d.get("preferred") == "tie" else "prev")
o1, o2 = side(a, "B"), side(b, "A")
res = dict(order1=dict(preferred=o1, margin_new_minus_prev=a and a.get("weighted_margin_B_minus_A"), strength=a and a.get("preference_strength")),
           swap=dict(preferred=o2, margin_new_minus_prev=(-b["weighted_margin_B_minus_A"] if b and b.get("weighted_margin_B_minus_A") is not None else None), strength=b and b.get("preference_strength")),
           calibrated=dict(overall=cal.get("overall_score"), verdict=cal.get("verdict"), model=cal.get("model")))
votes = [v for v in (o1, o2) if v]
if "new" in votes and "prev" not in votes:
    res.update(ship=True, decided_by="pairwise")
elif "prev" in votes and "new" not in votes:
    res.update(ship=False, decided_by="pairwise")
else:
    res["undecided"] = "split" if ("new" in votes and "prev" in votes) else "tie"
    t = side(tb, "B")
    res["tiebreak_critic"] = dict(preferred=t, model=tb and tb.get("model"), margin_new_minus_prev=tb and tb.get("weighted_margin_B_minus_A"))
    if t in ("new", "prev"):
        res.update(ship=t == "new", decided_by="tiebreak_critic")
    else:
        nq, pq = arg("--new-qa"), arg("--prev-qa")
        if nq and pq:
            n = {c["check"]: c["ok"] for c in json.loads(Path(nq).read_text())["checks"]}
            p = {c["check"]: c["ok"] for c in json.loads(Path(pq).read_text())["checks"]}
            common = sorted(set(n) & set(p))
            gained = [c for c in common if n[c] and not p[c]]; lost = [c for c in common if p[c] and not n[c]]
            res["gate_deltas"] = dict(common=len(common), gained=gained, lost=lost)
            res.update(ship=bool(gained) and not lost, decided_by="gate_deltas")
        else:
            res.update(ship=False, decided_by="no tie-break data")
(o / "ship.json").write_text(json.dumps(res, indent=2))
print("SHIP" if res["ship"] else "NO-SHIP", json.dumps(res))
