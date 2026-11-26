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

### Sky v8: SHIP

- **Render:** `renders/Sky_v8.mp4` (47.3 s). Source commit a324a07.
- **Pairwise vs v7:** both orders prefer v8, by +1.43 and +1.04, so it ships.
  - Blue light now visibly zig-zags and deflects in the scattering scene (0:16–0:20), where v7 drew a static straight line.
  - The ISS proof card has a callout on the scattered blue layer.
  - Crepuscular rays were added to the hook and to the callback.
  - The clipped container at the loop seam is fixed.
- **Calibrated:** 5.51 (v7 5.29), ONE MORE PASS. Scores: clarity 6, hook 6, loop 7, voice_captions 6, finish 6, concept_wow 5, design 5, motion 5, sound 5, style 5.
- **Gates:** 28/30 (v7 22/27 on the same r8 gates).
  - Now passing:
    - 0 caption ghost frames;
    - longest meaningful hold 1.27 s;
    - frame-1 hero 0.198, moved 0.182;
    - first line "SOMEONE ELSE'S BLUE SKY" (4 words);
    - clarity 7/7;
    - entrances: 0 snaps.
  - Still failing:
    - the end-card payoff settles for only 0.4 s before the loop (needs 1.5 s; the card itself runs 1.42 s);
    - labels_persist: "EVERY COLOR" stays readable in only 43 % of its shot.
- **Loop cost:** builder 3 runs, $1.31, about 51 min. Judge about 31 min on agy (free).
- **Calibrated rerun:** the first critic_deep produced no output (likely an agy timeout), so it was rerun once standalone.
- **Publish pack:** regenerated for v8 (`publish/03-sky/`, sha de86007461aeb2f8, 0 violations). Not uploaded. Felipe must review it and create `APPROVED`.
- **Hook proposal, not applied:** "Where does a sunset's missing blue end up?" (judge 4.25/5) needs Felipe's script approval. The Elevator proposal "Half the weight in an elevator shaft is hanging there for no one." is in the same state.

### New gates after the Elevator tie-break (commit 011b410)

- **`scripts/labels_persist.py` (hard gate in `qa.py`).** It OCRs the stage band at 2 fps (tesseract psm 11 + psm 3). Every label planned in `shots.md` must be read during its shot and stay readable for ≥ 60 % of the rest of the shot. The exception is a hand-over to a later label of the same shot. Validated on the tie-break: v6b PASS 15/15, v7 FAIL (MOTOR HELPS/HOLDS 0.38).
- **`scripts/vo_sync.py` (advisory only, `res.vo_sync_advisory`).** It checks for a pixel-motion event within ±0.4 s of each beat word. **It does not discriminate** (v6b 22/25, v7 23/25), because v7's lag is semantic (the wrong state is shown), not missing motion. It is kept as data, not as a gate.

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

## Round 9 candidates (generic, code-first)

1. **Atomic `<Label>`.** Text and its backing pill should be one component that animates as a unit: one transform, one opacity, never text without its backing. This prevents ghost text. The Sky v8 critic called it a **blocker** at 0:18, 0:32, 0:35 and 0:42, and the contrast min was 1.04. Add a lint that rejects raw text over a separately animated pill, plus a contrast gate on every frame of an entrance.
2. **End-card payoff length.** Payoff settled ≥ 1.5 s is already a gate, but builders keep adding motion that ends late (Sky v8 settled at 0.4 s). Fix it in structure: `EpisodeShell` freezes the payoff layout at `cardAt − 1.5 s`, or the tail gets a `[pause: …]`, which needs script approval.
3. **Semantic label-timing sync.** This replaces the pixel `vo_sync`. Each OCR label is tied to the spoken phrase it echoes (shared tokens, or an explicit `label@phrase` beat in `shots.md`). The label must appear within ±0.4 s of the aligned word, and the previous state's label must be gone. That needs OCR at 5 fps around beat windows only.
4. **Wow-moment hero framing.** Every episode's VIDEO.md has one "special moment". It should get a measured hero shot: subject ≥ 35 % of the stage, a camera push or scale change, ≤ 2 callouts, and a dedicated SFX hit. This addresses the critics' recurring "concept_wow 5" and "clipart in empty voids".
5. Smaller items:
   - an art-bbox edge gate (Elevator shaft art at x < 0);
   - a single automatic retry for ship-render infrastructure failures;
   - a longer `critic_deep` timeout;
   - ANC's 5 floating callouts;
   - QR clarity and holds.
