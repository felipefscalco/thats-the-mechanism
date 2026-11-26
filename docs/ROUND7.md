# Round 7: vendor-neutral roles, preview-first loop, new gates

Date: 2026-11-26 (BRT). Approved by the owner: "make it generic for several LLMs, not only Claude". Nothing is published.

## LLM role adapter (`scripts/llm.py`)
- Roles `planner`, `builder`, `fixer`, `critic`, `critic_deep`, `critic_tiebreak`, `clusterer` map to a provider and model in
  `pipeline.config.json` → `llm.roles`, with fallbacks. Override one run with `LLM_<ROLE>=provider:model`.
- Providers: `claude` (`claude -p --output-format json [--json-schema]`, prompt on stdin), `agy` (`agy -p --model … --json-schema FILE`),
  `codex` (`codex exec -C DIR -m M --sandbox read-only|workspace-write --output-schema FILE -o LAST`), `cursor-agent`
  (`cursor-agent -p --output-format json --model M --force | --mode ask`, schema goes in the prompt), `gemini-api` (critic only).
- One interface: prompt + workdir + scope globs + optional JSON schema + input files → `{ok, text, json, meta}`. A missing CLI falls
  through to the fallback list. `scripts/llm.py detect` and `roles` show what is installed and how roles resolve.
- The scope guard works for every provider: it snapshots the git work tree and reverts out-of-scope edits after the run. Tool caches
  and pipeline outputs are always allowed (`.remotion/`, `metrics/`, `qa/`, `renders/`, `_scratch/`). In r7 the guard first deleted
  Remotion's downloaded chrome-headless-shell, and that is fixed now.
- No script calls a vendor CLI directly. `builder.sh`, `ship_check.sh`, `critic.py --role`, `lessons.py` (clusterer) and
  `build_loop.py` all go through the adapter. Critics that cannot read video get 1 fps frame sheets and are told they have no audio.
- Claude token: an existing login, `CLAUDE_CODE_OAUTH_TOKEN`, or the `TTM_CLAUDE_TOKEN_FILE` file (default `~/.secrets/claude_oauth_token`).
  It is read into the child environment only.

### Providers tested
| Test | Provider:model | Result |
|---|---|---|
| JSON-schema smoke | claude:haiku, agy:gemini-3.8-flash-high | both returned schema-valid JSON (3.0 s / 14.9 s) |
| Planner (VIDEO.md for Sky) | claude:sonnet | 94 s, $0.27 list-equivalent |
| Builder / fixer / self-critique on Sky | claude:sonnet | see the Sky section |
| Critic, critic_deep (Sky ship) | agy:gemini-3.8-flash-high, agy:gemini-4-neon-high | see the Sky section |
| **Swap: builder** | agy:claude-sonnet-5-5 | edited IceDemo.tsx in 9.7 s. The scope guard reverted its out-of-scope README.md edit |
| **Swap: fixer** | agy:gemini-3.8-flash-high | asked for a size change plus a new `<Pill>`. `fixer_guard.py` REJECTED the structural insert, so the loop would revert the whole edit |
| **Swap: critic** | claude:sonnet (frame sheets, no audio) | Sky_v5 vs Sky_v6: preferred v6, strength 1, +0.53, in 31 s. agy had called it an exact tie twice in r6 |
| codex, cursor-agent | not installed | argv dry-run tests in `tests/test_r7_pipeline.py`; never logged in |

## Preview-first loop (`scripts/build_loop.py`)
plan (planner → frozen `episodes/<slug>/VIDEO.md`, outside the builder's scope) → build (key stills hook/mid/end first) →
`scripts/preview.py` (stills only) → route (value-only failures → fixer + `fixer_guard.py`, otherwise → builder) → builder
self-critique of the contact sheet → ONE full render + master + `qa.py` → `ship_check.sh`. Each role runs in a fresh session.
State is kept in `qa/<Id>/<SUF>/loop_state.json`. Infrastructure failures (render or QA crash) stop the loop and are not sent to the builder.

## New gates (A9b, A14+, A15 intro, A16–A18) and results on the r6 renders
Run with `qa.py --no-stems` (18 checks). The r6 renders were built from the same episode sources, so the probe passes are valid.

| Episode | r6 gates | r7 gates | New failures (all checked by eye on the frames) |
|---|---|---|---|
| QR_v6 | 17/17 | 17/18 | safe zone: a raw-SVG repair-byte cell sits in the platform column (x 892–936, y 950) at 10.6–11.6 s |
| Elevator_v6b | 17/17 | 14/18 | raw SVG floor markers L01–L08 and others below 4.5:1 (min 1.55); hook title block covers the L07 marker and sits 6 px from the MOTOR box (0–4.2 s); hook text past the top-right at 0.2 s; hand-rolled MOTOR badge snaps in (1.1 s, 2.4 s) |
| ANC_v7 | 17/17 | 17/18 | clutter: 4–6 tag labels at once (15.5–17.5 s NOISE/CHIP/ANTI-NOISE/SPEAKER; 29–32 s) |
| Sky_v6 | 17/17 | 14/18 | intro edge (SUNSET at x = 0, 0.4 s), hand-rolled badge snap (20.3 s), 4 callouts at 35.2–40.5 s, whole-stage cards (18.4–20.2 s, 42.4–46.2 s) |
| Sky_v5 (MP4-only gates) | – | framing FAIL | whole-stage cards at 4.8–6.8, 18.4–19.8, 42.4–46.2 s |
| ANC_v6 (calibration) | – | framing FAIL | boxed 78 % of the runtime; whole-stage card on most beats (the known slide-deck version) |

The Sky_v6 failures match the r6 critic's complaints almost one for one (clipped SUNSET, the four pills at 0:35, the slide-like ratio card).
The ANC_v7 clutter flag is a style call: those are diagram labels on TagLabels. Keep N = 3, or count only free-floating callouts.

## Sky (the r6 NO-SHIP)
- The planner wrote VIDEO.md from the script, shots, facts, and the r6 critic and gate findings. It asks for one continuous sky
  world with no cards or split panels, ≤ 3 callouts, and the 1/λ⁴ formula cut.
- Builder session 0 (claude sonnet, 1306 s, $1.81) rebuilt `Sky.tsx`. Preview it1 passed all 14 preview gates, and the self-critique changed nothing ($0.16).
- Ship render 1: 19/20, failing on SFX median 16.1 dB under the voice (limit ≤ 16). That went to the builder (145 s, $0.12). Preview it3 PASS, then ship render 2: **20/20 PASS**.
- Judge: pairwise Sky_v5 → Sky_v7 **SHIP in both orders**: +2.06 (strength 3/3, high) and swap +1.89 (3/3). Calibrated absolute critic (critic_deep, gemini-4-neon-high): **5.29, ONE MORE PASS** (Sky_v6 scored 5.39 on the same critic in r6). The caps it hit were linear fades without overshoot, static holds of 2–3 s, a generic 'slide-deck' look, the captions dimming at 0:38, and sound-off clarity (molecule scale, the shadow side).
- **Verdict: SHIP against Sky_v5 under the repo rule** (pairwise preference in both orders, all 20 gates pass; v5 fails the new framing gate). Sky is still below the 7+ bar on the absolute scale, so the next pass should take the critic's motion-craft and clarity fixes (`qa/Sky/v7/ship/critic_cal.md`).

## Time and usage vs r6
| | r6 (Sky) | r7 (Sky) |
|---|---|---|
| Per iteration | full render + master + QA ≈ 305 s (128 + 4 + 173) | preview ≈ 128 s (no encode, audio, stems, master): **−58 %** |
| Iterations | 12 full render+QA runs ≈ 61 min machine time | 3 orchestrator previews (+ the builder's own) + 2 full ships (236 s, 375 s) ≈ 17 min: **−73 %** |
| Builder LLM | 2 sessions, $0.69 list-equivalent; most iteration was driven by the orchestrating agent (r6 hit its usage limit) | planner $0.27 + builder $1.81 + fixes $0.21 + self-critique $0.16 = $2.45 list-equivalent, covered by the subscription. The loop is scripted, so no orchestrating-agent turns go into iterations |
| Critic | agy, 3 calls + retry | agy, 3 calls (no tie-break needed) |

Claude spend for Sky went up because this was a full rebuild (86k output tokens), not polish. The savings are in machine time and
in agent turns. The cost ledger is in `metrics/llm_calls.jsonl`.

## Known gaps
- The preview hold/cadence checks are approximations (0.2 s stills). The exact motion, audio and end-card gates run only at ship time.
- `static_gates` reads the current source, so its results on an old MP4 (Sky_v5) are not meaningful. Only the MP4 gates are compared in the tie-break.
- The builder's own `preview.py` runs share iteration numbers with the orchestrator's runs (it overwrites `preview_it<N>.json`).
