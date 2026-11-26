# Round 8: hooks, aligned captions, queue + publish pack, motion and clarity gates

Branch `r8` from main `b55657c`. Rules carried over from r7:
- Code and gates win over prose.
- Every LLM call goes through `scripts/llm.py` roles.
- Everything is generic for future episodes.
- Nothing is published.

The queue and publish pack design (items 5 and 6) was approved by Felipe before commit. The full guide is [`QUEUE_AND_PUBLISH.md`](QUEUE_AND_PUBLISH.md). The resume log is [`ROUND8_PROGRESS.md`](ROUND8_PROGRESS.md).

## What was built

| # | Item | Where | Notes |
|---|---|---|---|
| 1 | Hook step | `scripts/hooks.py gen\|check\|apply`, `prompts/hooks.md`, `prompts/hook_judge.md` | See [Hook step](#1-hook-step) below. |
| 2 | Script-aligned subtitles | `scripts/captions.py` | See [Script-aligned subtitles](#2-script-aligned-subtitles) below. |
| 3 | Kokoro pause tags | `scripts/script_text.py`, `scripts/tts.py` | `[pause: 0.4s]` in `script.txt` (allowed 0.05–3.0 s) inserts exactly `round(s*sr)` zero samples. `narration_segments.json` records each chunk's sample offsets, and caption timing uses them. |
| 4 | Credit ledger sanitising | `scripts/credits.py` (`check`, `sanitize`); `photos.py pick` uses it | Rows are rebuilt from a field whitelist. URLs are `http(s)` only, with no userinfo, fragment or query (except `curid`/`oldid`). Paths are made repo-relative, and tokens and local paths are scrubbed from text. CSV is written atomically with LF line endings, hand-written md notes are kept, and **a persistence failure never breaks a render** (it returns False). |
| 5 | Batch topic queue | `scripts/pipeline.py` | `--batch topics.jsonl --stop-at plan\|hooks\|script\|audio\|preview\|ship`. Preflight runs before any LLM spend (exit 2). State is resumable per topic in `queue/state/`, and a failing topic doesn't block the others. |
| 6 | Publish pack | `scripts/publish.py pack\|verify\|upload` | `publish/<slug>/` holds the video, per-platform text within limits, the YouTube synthetic-media flag (made-for-kids false), credits and `review.md`. **No upload.** Felipe creates `APPROVED` with the pack sha; the stub refuses anyway. |
| 7 | Motion and clarity gates | `scripts/qa.py`, `preview.py`, `static_gates.py`, `entrances.py`, `clarity.py`, `contrast.py`; `brand/Chrome.tsx`, `brand/Kit.tsx` | See [Gates](#7-gates-measured-preview-and-full-render) below. |

### 1. Hook step

- The `hooks` role writes 3–5 candidates mixing four patterns: curiosity gap, visual pattern interrupt, specific question and careful contrarian.
- Code rules filter the candidates:
  - a ban list: "hey guys", "today I'll show you", "in this video", "wait, don't scroll", "you won't believe", "secret", and others;
  - at most 16 spoken words, and at most 7 words on the first on-screen line;
  - a curiosity-gap signal (heuristic);
  - a payoff quote that appears later in the script (similarity ≥ 0.85), with overlapping key terms.
- The `hook_judge` role scores the survivors (gap, payoff, visual, specific, honest) and can veto them.
- Outputs: `hooks.json`, `hooks.md` and `script.hook.txt`. `apply` only works while the script is not approved.

### 2. Script-aligned subtitles

- Whisper words are aligned to the known script with a word-level Levenshtein DP (1:2 and 2:1 merges). Numbers are expanded to spoken form, including ranges ("40–50%" becomes "forty to fifty percent"), then merged back to the written form.
- The whisper initial prompt is "Glossary: …", built from the script's technical terms plus an optional `terms.txt`.
- Captions are always the script words.
- The step fails when any of these limits is exceeded:
  - word match < 90 %;
  - an unmatched run > 3 words;
  - a word outside its TTS chunk.
- Output: `captions_align.json`.

### 7. Gates (measured, preview and full render)

| Gate | Rule |
|---|---|
| Caption ghost frames | Any dimmed caption frame while a word is spoken fails. |
| Meaningful-motion hold | A structure-level change at least every 1.75 s. Particles and drift don't count, and the end hold is excluded. |
| Entrance easing | Covers **all** elements (`entrances.py`): no snaps, and at most 2 opacity-only fades. |
| Frame-1 hook | Hero ≥ 8 % of the stage, ≥ 5 % of pixels moving in 0.33 s. |
| First speech | ≤ 0.5 s. |
| First on-screen line | ≤ 7 words. |
| Sound-off clarity | Each causal sentence needs a keyword that appears both in `shots.md` and in the tsx. |
| Clutter | Counts only **floating** callouts. A pill touching an art component (≥ 25 px, within 8 px) is attached and not counted. |

Component changes:
- **Caption dimming root cause.** The caption page entered with `opacity: min(1, s*1.5)` on every page change, which gave 2–3 ghost frames per page. Episodes had 45–56 such frames, including the 0:38 dim the critic flagged on Sky. The fade was removed (a scale-only entrance), and the ghost-frame gate now checks for it.
- **`<Enter>` component.** Anticipation, then overshoot; opacity changes only during the first 25 %.

The clutter mode is configurable in `pipeline.config.json` → `qa_gates.clutter.count` (`floating` | `all`). The default is **floating**. **Felipe has not decided yet.**

## Roles added (`pipeline.config.json` → `llm.roles`)

`hooks` (claude:sonnet), `hook_judge` (claude:haiku; agy timed out at 200 s), `writer` (claude:sonnet), `publisher` (claude:haiku). Each has fallbacks. The builder's scope now includes `episodes/<slug>/shots.md`, because the clarity gate and the first-line gate read it.

## Gate results on existing renders (r8 gates, before fixes)

| Episode | Fails |
|---|---|
| Sky v7 | caption ghosts, motion hold (2.33 s at 15.9 s, and others), frame-1 hook (moved 1.6 %), first line 8 words, clarity 6/7 |
| QR v6 | ghosts, hold 3.5 s at 30.6 s, an entrance snap at 43.8 s, clarity 7/9, a safe-zone hit at 10.6 s |
| Elevator v6b | ghosts, holds 2.37 s and 2.17 s, floor-marker contrast, hook text at the edge (0.2 s), hook-title occlusion (0–4.2 s), badge snaps, entrance snaps, clarity 7/8 |
| ANC v7 | ghosts, 5 floating callouts at 30.8–31.7 s (real crowding) |

Old renders still show the ghosts. A re-render with the fixed `Chrome.tsx` removes them (Elevator v7: 0 ghost frames).

## Episodes

### Elevator v7: NO SHIP

- **Gates:** 28/29 pass; v6b failed 8. The one remaining failure is entrance snaps: the orange bar segment at 17.2 s and the end-scale card edges at 39.9 s.
- **Pairwise:**
  - order 1 prefers v6b (−0.74);
  - the swap prefers v7 (+0.96);
  - the tie-break critic (gemini-4-neon) prefers **v6b** (−0.37).
- **What v7 fixed and broke:** it fixes the floor-marker collisions, the hook-title overlap and the LOAD pill at the edge. But it loses the CAR/CW bar labels, lags the voice-over at 0:19–0:26, and clips the car's left edge at 0:11–0:13.
- **Calibrated:** 5.64 (v6b 5.60), ONE MORE PASS.
- **Source:** v7 is kept on branch `r8-elevator-v7-candidate`. `main` keeps the v6b source.

### Sky

- **Hook proposal:** "Where does a sunset's missing blue end up?" (judge 4.25/5).
- **Elevator hook proposal:** "Half the weight in an elevator shaft is hanging there for no one."
- **Not applied.** Both scripts are approved (script gate), so changing the narration needs Felipe's approval.
- **The v8 pass is the next step.** Its task is in `qa/tasks/r8_sky_v8.md`:
  - a moving frame-1 hero;
  - a first line of ≤ 7 words;
  - a "BLUE SCATTERED OUT" keyword;
  - motion beats;
  - `<Enter>` entrances;
  - the critic's geometry and scale-truth fixes.

  Command:

  ```bash
  .venv-tts/bin/python scripts/build_loop.py Sky 03-sky v8 --prev renders/Sky_v7.mp4 \
    --prev-qa qa/Sky/r8gates_v7/report_it1.json --task-file qa/tasks/r8_sky_v8.md
  ```

### Queue demo

Topics: a microwave topic, a broken topic and an unapproved one.
- The unapproved topic was skipped.
- The broken topic failed at `plan` without blocking the others.
- The microwave topic ran `plan` (writer, $0.12) and `hooks` (chosen: "Why is your microwave leftover scalding in one spot and frozen in another?", $0.05), then went to **waiting** on the facts gate.

## LLM usage (r8, from `metrics/llm_calls.jsonl`)

| Role | Provider:model | Calls | $ | Wall |
|---|---|---|---|---|
| builder | claude:sonnet | 3 | 1.20 | 1900 s |
| planner | claude:sonnet | 1 | 0.35 | 115 s |
| hooks | claude:sonnet | 4 | 0.23 | 34 s |
| writer | claude:sonnet | 1 | 0.12 | 21 s |
| hook_judge | claude:haiku | 4 | 0.02 | 66 s |
| publisher | claude:haiku | 3 | 0.01 | 20 s |
| critics / tie-break / calibrated / clusterer | agy (gemini) | — | 0 (free) | ~25 min |

The total Claude spend is about **$1.93**.

## Open issues

- **Elevator:** run one more pass from the candidate branch. Restore the CAR/CW labels, keep beats locked to the voice-over at 0:19–0:26, keep the car inside the stage, and fix the bar-segment and end-card entrances. The calibrated critic also wants more camera variety (81 % of the runtime is one schematic) and mechanical foley.
- **Art edge clip has no gate:** the edge gate checks labels only, but the critic saw shaft art at x < 0. Add an art-bbox edge gate.
- **The first Elevator ship render failed once in QA** (`stem_sfx.wav` "System error"). It was transient and passed when the loop was resumed. Make the loop retry infrastructure failures once.
- **Hook proposals for Sky and Elevator** are waiting for Felipe's script approval.
- **Clutter mode** (floating vs all) is waiting for Felipe's decision.
- **ANC** has 5 floating callouts at 30.8–31.7 s.
- **QR** fails clarity (38.3 s and 41.1 s) and has holds.
- **The Sky publish pack** in `publish/03-sky/` is for v7. Regenerate it after a shipped v8.
