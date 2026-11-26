# Round 6 — Claude Code builder + Antigravity (`agy`) critic

Date: 2026-11-25 → 2026-11-26 (BRT). Round 6 wired both CLIs into the pipeline, added three QA gates, and rebuilt all four episodes under the new gates.
Nothing here is published; the human approval gate for publishing is unchanged.

## Roles (see `TESTS_CLI.md`)
- **Builder:** `scripts/builder.sh` runs `claude -p`. Scope is limited to `remotion/src/episodes/<ID>.tsx` and `episodes/<slug>/`. It injects `docs/active_rules_prompt.txt` and iterates until `scripts/qa.py` passes.
- **Judge:** `scripts/ship_check.sh` runs `agy` (Antigravity). The builder never judges its own render.
  - Pairwise `gemini-3.8-flash-high`, both orders (prev vs new, and swapped).
  - Calibrated `gemini-4-neon-high` with the QA report.
  - Then `scripts/lessons.py` merges the critic's `general_rules` into `docs/STYLE_RULES.md`.
- **SHIP rule:** the new render must be preferred in at least one order and never lose in the other (ties allowed).

## New gates (now 17 checks in `qa.py`)
| Gate | Where | Why |
|---|---|---|
| A13 icon/label clearance ≥ 36 px | `contrast.py` + `Kit.tsx` `Lane` / `LabeledBox` | the `CHIP` label was covered by an icon at 16 s in ANC_v6 and nothing caught it |
| A14 badge entrance pop (anticipation + overshoot) | `contrast.py` + `Kit.tsx` `TagLabel`, `PROBE_OCC` | stops flat popping badges |
| A15 text ≥ 24 px from the left/right frame edge (held ≥ 0.6 s) | `contrast.py` `unsafe()` (`EDGE=24`) | the critic found "CAR vs CW" pushed off the left edge in Elevator_v6; the old gates passed it |

## Results
| Episode | Final render | Gates | Ship vs previous | Calibrated (neon) |
|---|---|---|---|---|
| 01 QR | `QR_v6.mp4` | 17/17 (edge re-QA 15/15 with `--no-stems`, SFX checks from it2) | **SHIP** vs QR_v5: new +0.50 (s2) / swap +1.00 (s2) | 4.98 ONE MORE PASS |
| 02 Elevator | `Elevator_v6b.mp4` (it5) | 17/17 | **SHIP** vs Elevator_v5: new +0.62 (s2) / swap +1.64 (s3). The earlier `Elevator_v6.mp4` (it4) was NO-SHIP (split verdict: unlabeled down-arrow contradicted the rise at 31 s). | 5.60 ONE MORE PASS |
| 03 Sky | `Sky_v6.mp4` (it5, one over the ~4 iteration cap) | 17/17 | **NO-SHIP**: tie in both orders, run twice, margin 0.0. v6 passes the new A13–A15 gates (v5 was not re-QA'd against them). | 5.39 ONE MORE PASS |
| 05 ANC | `ANC_v7.mp4` (it2) | 17/17 | **SHIP** vs ANC_v6: new +1.63 (s3) / swap +2.17 (s3) | 5.53 ONE MORE PASS |

No calibrated score reached SHIP-level ("ONE MORE PASS" everywhere). Absolute scores are not comparable across episodes; the pairwise verdict is what gates shipping.
Sky was not iterated again this round, by decision. Its critic reasons are identical on both versions (clutter of four callout pills at 0:35, radial rays crossing the `~1000× SMALLER` badge at 0:12, dense Rayleigh formula beat at 0:18).

## Candidate gate gaps found
1. **Raw SVG `<text>` is not contrast-scanned.** Elevator floor markers L01–L08 measured as low as 1.55:1 and `contrast.py` does not see them.
2. **Hand-rolled badges are invisible to the pop gate.** It only tracks cyan backings (`TagLabel` / `Pill` / `TitleHook`).
3. **Transient clips under 0.6 s pass.** Sky's `SUNSET` label is briefly clipped at the left edge during the intro move at 0.3 s.
4. **Critic flags on ANC_v7 that no gate measures:** frozen holds of more than 2 s (earcup 6–9 s, waves 12–14 s), a loop seam with a ~35% larger zoom and a chapter bar showing `05/05` instead of `01/05`, and the same whoosh on every cut. The critic samples at 1 fps, so these need a human or a probe check before being promoted to gates.
5. **Pairwise critic returns exact ties** on near-identical cuts (Sky). Add a tie-breaker, such as per-gate deltas from `qa.py`, before declaring NO-SHIP.
6. `lessons.py` still lists the badge-pop rule under "Candidate gates" although A14 implements it.

## Operational notes
- Claude Code builder passes cost about 15 minutes per episode and need about 3 iterations. Run at most 2 renders at a time (RAM).
- The agy calibrated call can take 6+ minutes; the pairwise calls take about 2 minutes each, in parallel.
- Round 6 was interrupted by usage limits more than once; `ROUND6_PROGRESS.md` (in the working tree, not committed) was the resume file.
