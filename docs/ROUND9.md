# Round 9: atomic labels, payoff hold, label sync, hero gate, art edge gate. QR v7 ships.

Branch `r9`, cut from main `e6c2c47`, then fast-forwarded into main. Owner decisions:
- Keep the current hooks; there is no script or narration change, and the hook proposals stay unused.
- The clutter gate counts floating callouts only. This is recorded in `pipeline.config.json` → `qa_gates.clutter.decided`.
- **Scope change (Felipe, mid-round):** round 9 re-renders **QR only**. ANC, Elevator and Sky are deferred. Their task files are ready in `qa/tasks/r9_*.md`.

## What was built (code and gates; all generic for future episodes)

| # | Item | Where | Calibration |
|---|------|-------|-------------|
| 1 | **Atomic labels.** Text and its backing are one transformed group, and `o` is the scale-pop progress, never opacity. New `Badge` handles hand-made backings. `Enter`, `Pill` and `TitleHook` no longer fade, and `popOpacity` is binary. The static gate `text: atomic labels only` fails on any raw `<text>`/`<tspan>` in an episode. QR and Elevator were migrated. | `remotion/src/brand/Kit.tsx`, `timing.ts`, `scripts/static_gates.py` | — |
| 1b | **Ghost-text gate.** A see-through label sample (< 3:1) next to that label's readable state, outside transitions, fails. | `scripts/contrast.py`, `qa.py` | Matches the Sky v8 critic's flagged times |
| 2 | **Payoff hold.** `EpisodeShell` freezes the stage for `PAYOFF_HOLD_S = 1.5` s before the loop whip. `mix_one.sh` pads the audio tail so the hold fits. The static gate is `payoff: >= 1.5 s settled hold`. | `EpisodeShell.tsx`, `scripts/mix_one.sh`, `qa_gates.payoff` | — |
| 3 | **Word→label sync.** Every OCR label that echoes a spoken phrase must first appear within ±0.5 s of the word, using the aligned captions. A `LABEL @spoken phrase` entry in shots.md sets the echo explicitly. The OCR is parallel with `OMP_THREAD_LIMIT=1`, and labels_persist dropped from about 6 s per call to about 18 s total. | `scripts/label_sync.py`, `shotlib.py`, `labels_persist.py` | Elevator: v7 is better than v6b on label timing |
| 4 | **Hero gate.** shots.md marks exactly one `hero@<spoken phrase>` beat (static gate). On the render, the hero subject must be ≥ 35 % of the stage, centred (dx ≤ 15 %, dy ≤ 20 %), moving (no still > 1.0 s), on screen ≥ 1.5 s, and not edge-clipped. | `scripts/hero.py`, `static_gates.hero_marked` | Sky v8 PASS (size 0.385, motion 0.22). Sky v7 FAIL (still 1.5 s). Elevator v6b "It would rise" FAIL (1.36 s) |
| 5a | **Art edge gate.** A foreground object whose fill runs past a side edge (more than 90 px of edge, held ≥ 0.6 s outside transitions) fails. Thin beams from off-screen are allowed. | `scripts/artedge.py`, `qa.py` | Elevator v7 FAIL at 11–14 s (the critic's "shaft off-screen"). Elevator v6b, Sky v8, QR v6 and ANC v7 PASS. A synthetic 40 px shift FAILs |
| 5b | **Single infra retry.** A ship render or QA crash is retried once before `build_loop` stops. | `scripts/build_loop.py` | — |
| 5c | `critic_deep` timeout raised from 300 s to 1800 s. | `pipeline.config.json` | The agy deep critic takes 13–27 min |
| — | The builder prompt lists the r9 rules, and builders may edit `shots.md` (it must describe what is drawn). | `prompts/builder.md` | — |

## r9-gate baseline on the current main renders (before fixes)

Reports are in `qa/<Id>/r9base_<suf>/report_it900.json`. Out of 35 checks, the hard fails were QR v6: 11, ANC v7: 9, Elevator v6b: 12, Sky v8: 8.
- Every episode fails the hero gate, because no beat is marked yet.
- Most episodes fail label_sync and ghost text. The main exceptions are ANC (5 callouts at 30.8 s) and Elevator (contrast, safe zone, clearance).

## Episodes

### QR v7: SHIP (`renders/QR_v7.mp4`, render not committed)
- Loop: `scripts/build_loop.py QR 01-qr-code v7 --prev renders/QR_v6.mp4 --prev-qa qa/QR/r9base_v6/report_it900.json --task-file qa/tasks/r9_qr_v7.md --plan-extra-file qa/tasks/r9_plan_extra_qr.md`.
- Steps:
  1. The planner wrote `episodes/01-qr-code/VIDEO.md`.
  2. The builder's preview passed on the first try.
  3. Self-critique made changes, and the preview passed again.
  4. Ship render it101 failed 3 gates (motion cadence, entrances, labels-persist). They went back to the builder.
  5. Ship render it102 failed 2 gates (labels-persist; label_sync on STILL PLAYING +0.56 s, LEVEL H +1.52 s, 30 % REBUILDABLE +0.98 s).
  6. The judge then ran.
- **Judge:** pairwise prefers the new render in **both orders**: margin +1.74 (order 1), +2.03 (swap), strength 3. The decision came from the pairwise step.
- **Calibrated (gemini-4-neon-high):** **5.35**, verdict ONE MORE PASS. QR v6 scored 4.98.
  - Hook 5→6, motion 4→5, style 5→6.
  - The other axes are unchanged: clarity 5, concept 5, design 5, finish 6, loop 5, sound 5, voice/captions 6.
- Top v7 weaknesses from the critic:
  - The 3-line caption at 0:13 collides with the chapter deck.
  - The hero beat reuses the hook's QR card.
  - The 24-box byte grid is static from 0:12 to 0:18.
  - The hook title box overlaps the QR's top-left finder.
- Publish pack: `publish/01-qr-code/` (sha `08d2ec5a8cadb5c5`, 0 violations). **Nothing uploaded.** Posting needs a Felipe-created `APPROVED`.

### ANC v8, Elevator v8, Sky v9: deferred (owner scope change)
- Ready to run: `qa/tasks/r9_anc_v8.md`, `r9_elevator_v8.md`, `r9_sky_v9.md`, plus `r9_plan_extra_*.md`.
- `_scratch/r9/run_loops.sh` holds the exact sequential commands. Run them one at a time, never in parallel, because of the scope guard.

## LLM usage (QR v7 loop, from `metrics/llm_calls.jsonl`)

| role | provider:model | calls | wall | cost |
|------|----------------|-------|------|------|
| planner | claude:sonnet | 1 | 1063 s | $0.70 |
| builder (build, self-critique, fix) | claude:sonnet | 3 | 4615 s | $1.94 |
| critic (pairwise ×2) | agy:gemini-3.8-flash-high | 2 | 263 s | $0 (free tier) |
| critic (calibrated) | agy:gemini-4-neon-high | 1 | 246 s | $0 |
| clusterer (lessons) | claude:haiku | 1 | 175 s | $0.03 |
| **total** | | 8 | **6361 s LLM** (loop wall about 1 h 55 min, including renders) | **$2.67** |

## Open issues
- **Preview and ship disagree.** Preview passed twice, but the full render then failed motion cadence, entrances and label gates. The still-based preview approximations, especially for cadence and label timing, are too loose. Either run label_sync and labels_persist on a cheap low-res preview render, or tighten the preview cadence.
- **QR shipped with 2 hard gates still failing** after MAXS=2: labels_persist and label_sync. The current policy lets the judge decide after the ship cap. Decide whether a hard-gate failure should block the ship.
- **labels_persist conflicts with planned label swaps.** BYTES GO MISSING → MISSING BYTES: REBUILT in one shot fails "stays through its shot". shots.md needs per-label windows (or `@phrase` end times) so a planned swap can pass.
- **Caption safe zone.** The critic's top QR v7 blocker is a 3-line caption at 0:13 colliding with the chapter deck. There is no gate for caption line count or caption-to-deck clearance yet.
- **Hero reuse.** The hero gate measures size and motion, but not novelty (the hero reuses the hook's card). A possible check: hero-window frames must differ from the hook frames.
- ANC, Elevator and Sky have not been re-rendered on the r9 loop (deferred). Their current renders fail the new hero gate until a beat is marked.

## Next steps / deferred ideas
- **Deferred (Felipe):** a speed A/B, not run. Per Anthropic's "Using Claude Opus 5.5 as your daily driver":
  - try Opus 5.5 at Medium effort for planner, builder and critic_tiebreak instead of Sonnet, since a stronger model can finish with less exploration;
  - keep Haiku/Sonnet for cheap, well-scoped roles;
  - remove "think hard/carefully" phrasing from role prompts;
  - state the finished output and the stop condition up front;
  - attach stills and images instead of transcribing values;
  - name the specific styles to avoid.
  
  Validate it with an A/B on one episode, measuring wall time, cost and verdict.
- Run the deferred ANC, Elevator and Sky loops using the ready task files.
