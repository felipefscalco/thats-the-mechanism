# Round history

Short, factual summary of rounds 1–9. Full reports, scores, and iteration notes live in the linked docs — do not copy them here. Nothing in any round was published.

**Versions on `main` after round 9:** QR v7, Elevator v6b, Sky v8, ANC v7. Elevator v7 (round 8) was not shipped; its source lived on branch `r8-elevator-v7-candidate`.

Calibrated critic scores are advisory and sit in the mid-5s (“ONE MORE PASS”). They are not comparable across episodes. **Shipping is decided by the pairwise critic**, not by the absolute score. The informal “7+” bar has not been reached.

## Round 1 (2026-11-25, initial import)

First local pipeline: fact-checked English scripts, Kokoro TTS, whisper.cpp captions, original Remotion animation, Kenney CC0 SFX. Pilot compositions QR, Elevator, Sky. Catchphrase required in the script. Early stills and first renders; hook and safe-zone issues showed up immediately.

See the initial import commit and later port notes in [`ITERATIONS.md`](../ITERATIONS.md).

## Round 2 — render → review → fix

Documented in [`ITERATIONS.md`](../ITERATIONS.md). Introduced `scripts/iterate.sh`, visual review of grid and transition contact sheets, and tighter motion/hook detectors. Typical local stage times (also in the README): TTS 7–8 s, captions 6–7 s, render 26–35 s, QA 39–49 s; about 1.5 minutes of machine time per episode plus the review loop. Three candidates took 5–7 QA iterations each. A kit fix from the `IceDemo` loop-seam failure faded captions and the chapter label across the loop frames.

## Round 3 — depth, SFX density, tool A/B

Documented in [`ITERATIONS.md`](../ITERATIONS.md) (v3 section) and [`METRICS.md`](../METRICS.md). Parallax depth layers, automatic camera SFX, papercut cues, an upgraded Elevator ending, a 3D Earth on Sky (later replaced). ffmpeg-normalize mastering landed in this era. **Qwen3-TTS was tested and not adopted** (slow on CPU, not clearly better).

## Round 4 — Look A, licensed photos, TitleHook

Style-frame step; owner chose **Look A** + drawn backdrops. Real PD/CC0 `ProofCard` photos with source verification. Title-as-hook grammar, WCAG label contrast probe, SFX density 1.2–1.5/s, independent Gemini critic (key from the environment only). v4 approved over earlier looks. Metadata and photo credits: [`metadata.md`](../../metadata.md).

## Round 5 — toggleable gates, fact ledger, calibrated critic

Report and resume: [`ROUND5_PROGRESS.md`](../ROUND5_PROGRESS.md), [`TESTS_R5.md`](../TESTS_R5.md), [`LESSONS.md`](../LESSONS.md) (L-21–L-27). Fact ledger blocks TTS until spoken numbers are verified. Storyboard stills before a full render. New gates: raw font size, cadence, pre-catchphrase silence, Shorts safe zones. Emil easing, shotcraft punch, TagLabel, FlatPlanet, grain, UISFX, Phosphor icons.

**v5:** QR, Elevator, and Sky all passed then-current automated checks. Pairwise (lite, after free-tier quota exhaustion): QR tie, Elevator and Sky preferred v5. Calibrated scores barely moved. Lesson L-22: budget Gemini free-tier calls (20/model/day) when using `gemini-api`. Absolute calibrated scores do **not** reliably rank versions (T11).

## Round 6 — Claude Code builder + Antigravity critic

Full report: [`ROUND6.md`](../ROUND6.md). Builder via `claude -p`; judge via `agy`. New gates A13–A15 (icon/label clearance, badge pop, side-edge margin). All four episodes rebuilt.

| Episode | Render | Gates | Pairwise vs previous | Calibrated |
|---|---|---|---|---|
| QR | v6 | 17/17 | **SHIP** (+0.50 / +1.00) | 4.98 |
| Elevator | v6b | 17/17 | **SHIP** (+0.62 / +1.64). Earlier v6 was NO-SHIP (unlabeled down-arrow). | 5.60 |
| Sky | v6 | 17/17 | **NO-SHIP** (tie both orders, twice) | 5.39 |
| ANC | v7 | 17/17 | **SHIP** vs ANC v6 (+1.63 / +2.17) | 5.53 |

Gaps found here (raw SVG contrast, hand-rolled badges, short clips, critic ties) drove round 7. Builder ~15 minutes per episode; the round was interrupted by usage limits more than once.

## Round 7 — vendor-neutral roles, preview-first loop

Full report: [`ROUND7.md`](../ROUND7.md). `scripts/llm.py` role adapter; preview-first `build_loop.py`; scope and fixer guards; new framing, clutter, SVG contrast, intro-edge, and HUD gates. Claude token path became configurable (`TTM_CLAUDE_TOKEN_FILE`).

Sky was rebuilt from a frozen `VIDEO.md` (**v7 SHIP** vs v5 in both orders, +2.06 / +1.89, 20/20 gates, calibrated 5.29). Machine time per Sky iteration dropped about 58%; the full Sky loop ~17 min vs ~61 min in round 6. List-equivalent Claude spend is an estimate, not a card charge when a subscription token is used. Provider swaps (Antigravity as builder/fixer, Claude as critic) worked; Codex and cursor-agent were dry-run only (not installed).

New r7 gates on the r6 renders found real issues (QR label near the edge; Elevator contrast and overlap; Sky clipped “SUNSET” and slide-like cards; ANC 4–6 labels at once).

## Round 8 — hooks, aligned captions, queue, publish pack

Full report: [`ROUND8.md`](../ROUND8.md). Hook step; script-aligned captions; Kokoro `[pause: Ns]` tags; credit sanitising; batch queue; review-only publish pack; motion and clarity gates. Caption ghosting was traced to a per-page fade in `Chrome.tsx` and fixed.

**Elevator v7: NO SHIP.** 28/29 gates (v6b had failed 8) but the critic still preferred v6b by a slim tie-break (−0.37). v7 lost bar labels, lagged the voice-over at 0:19–0:26, and clipped the car. Source kept on `r8-elevator-v7-candidate`. This showed the tests were still missing label persistence and semantic narration sync.

**Sky v8: SHIP** vs v7 in both orders (+1.43 / +1.04). Gates 28/30 vs v7 22/27. Calibrated 5.51 (was 5.29). Moving frame-1 hero, ≤7-word hook line, keyword labels, eased entrances. Remaining issues: ghost contrast during some label entrances (min 1.04; text appearing before its backing) and a weak impact moment; end-card payoff settled only 0.4 s. Publish pack in `publish/03-sky/` for review only.

QR and ANC were **not** rebuilt in round 8; they only ran the new tests (QR: holds, an entrance without easing, a label near the edge; ANC: 5 floating callouts around 0:31).

New hard gate `labels_persist`; `vo_sync` is advisory only (it did not catch Elevator v7's semantic lag).

## Round 9 — atomic labels, payoff hold, sync, hero and edge gates; QR v7 ships

Full report: [`ROUND9.md`](../ROUND9.md). Branch `r9` was cut from `e6c2c47` and fast-forwarded into main (`40c17bb`). Settled earlier in the round: keep the current hooks; the clutter gate counts floating callouts only.

Generic kit (for future episodes too): atomic labels (text and backing are one transformed group; a ghost-text gate matched the four Sky v8 critic instants); a 1.5 s payoff hold before the loop whip, with audio tail padding; word→label sync within ±0.5 s (`label_sync.py`); a hero gate (exactly one `hero@` beat, size, centering, motion); an art-edge gate (it failed Elevator v7's car at 11–14 s, and passed v6b / Sky v8 / QR v6 / ANC v7); one retry for a ship-render or QA infrastructure crash; `critic_deep` timeout raised to 1800 s.

r9-gate baseline on the then-current renders (35 checks, hard fails): QR v6 11, ANC v7 9, Elevator v6b 12, Sky v8 8. Every episode failed the hero gate until a beat was marked.

**Scope change (Felipe, 2026-11-26, mid-round):** re-render **QR only**. ANC, Elevator, and Sky were deferred; their task files are in `qa/tasks/r9_*.md`.

**QR v7: SHIP** vs v6 in both orders (+1.74 / +2.03, strength 3). Calibrated **5.35** (v6 was 4.98), ONE MORE PASS. Hook 5→6, motion 4→5, style 5→6. Shipped with two hard gates still failing after the ship-iteration cap: `labels_persist`, and `label_sync` on STILL PLAYING, LEVEL H, and 30 % REBUILDABLE. Under the 2026-11-26 decision, hard-gate failures do **not** block a ship once that cap is hit; the pairwise judge decides, as they did here. The critic's top remaining weaknesses: a 3-line caption collides with the chapter deck at 0:13; the hero reuses the hook's QR card; a static 24-box byte grid from 0:12–0:18; the hook title overlaps the top-left finder. Publish pack: `publish/01-qr-code/` (review only, nothing uploaded). Loop wall about 1 h 55 min; list-equivalent Claude spend about $2.67.

A planned Opus 5.5 speed A/B was deferred, not run. See [`ROADMAP.md`](ROADMAP.md).
