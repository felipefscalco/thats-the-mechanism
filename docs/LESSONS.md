# Lessons learned (review log)

Every reviewer (human or any LLM/agent) MUST read this file before working on an episode or the brand kit, and MUST append to it after each review.

## How to log
One entry per finding. Newest at the bottom. Format:

```
### L-<number> · <YYYY-MM-DD> · <episode or "kit"> · <severity: blocker|major|minor>
- Problem: what was wrong (observable, e.g. "label clipped at right edge at 0:12").
- Root cause: why it happened (code/kit/script decision).
- Fix: what changed (file + short description), or "open".
- Prevention: the rule, check, or kit change that stops it repeating. Prefer an automated check in scripts/qa.py or docs/ACCEPTANCE.md over a prose rule.
- Status: fixed | open | wontfix (reason)
```

## Rules
- Before reviewing, scan Prevention lines; check the episode against each one.
- A finding that already has an entry is a regression: reopen that entry, mark severity at least major, and add an automated check if there was none.
- When a Prevention becomes an automated check or kit default, write where (e.g. "qa.py: motion_gap").
- Suggestions/ideas that are not bugs go to docs/BACKLOG.md, not here.

## Entries (seeded from rounds 1-2, see docs/ITERATIONS.md)
### L-1 · 2026-11-25 · kit · major
- Problem: camera punch pushed art into captions/brand bar.
- Root cause: labels lived on the camera layer.
- Fix: verdict labels moved to a camera-locked layer.
- Prevention: overlays and labels never on the camera layer; QA safe-zone check.
- Status: fixed
### L-2 · 2026-11-25 · kit · major
- Problem: 2.5-8.4 s stretches with no motion.
- Root cause: shots planned per sentence, not per beat.
- Fix: added beats; motion gate.
- Prevention: motion never stalls > 2 s (qa.py motion check); beat every <= 3 s in the shot table.
- Status: fixed
### L-3 · 2026-11-25 · Elevator · minor
- Problem: elements in the platform right-hand button column.
- Root cause: layout ignored platform UI.
- Fix: bars re-centred.
- Prevention: respect safe zones in docs/STYLE_BRIEF.md.
- Status: fixed
### L-4 · 2026-11-25 · kit · major
- Problem: loop broke (captions/chapter label lingering in last frame; template loop bug).
- Root cause: outro did not reset overlays.
- Fix: shared loop code fixed; overlays cleared before whip.
- Prevention: QA first/last frame PSNR >= 45 dB.
- Status: fixed

## Round 3 entries
### L-5 · 2026-11-25 · Elevator · major
- Problem: an SFX peak only 6.7 dB under the voice at 0:31 ("It would rise").
- Root cause: once camera moves started emitting SFX automatically, the camera punch (stamp+glint) landed on top of the hand-placed whoosh 0.9 and reveal 0.8.
- Fix: Elevator.tsx rise cues lowered (whoosh 0.6, reveal 0.5).
- Prevention: when adding hand cues on a frame that has a camera punch, assume stamp+glint are already there. qa.py "SFX ... none louder than voice-8 dB" catches it.
- Status: fixed
### L-6 · 2026-11-25 · QR · minor
- Problem: SFX onset density 1.85/s (target 1.2–1.5, clutter risk).
- Root cause: micro-ticks plus automatic camera SFX were added on top of the dense v2 tick runs (6-tick "cut" run).
- Fix: micro-tick exclusion window 6 → 10 frames (EpisodeShell.tsx); QR tick run 6 → 3. Now 1.77/s.
- Prevention: qa.py "SFX onset density 1.0-1.8 /s" (new automated check). QR is still above 1.5, see BACKLOG.
- Status: fixed (within gate)
### L-7 · 2026-11-25 · kit · major
- Problem: mastered MP4s had 96 kHz AAC audio.
- Root cause: ffmpeg-normalize (loudnorm) upsamples internally and keeps that rate unless told otherwise.
- Fix: scripts/master.sh passes `-ar 48000`.
- Prevention: qa.py format check now requires sample_rate 48000.
- Status: fixed
### L-8 · 2026-11-25 · Sky · minor
- Problem: "SOMEONE ELSE'S AFTERNOON" (blue text) was low-contrast over the new 3D planet's blue ocean.
- Root cause: label colour was chosen against the old dark-green SVG Earth; swapping the hero art changed what sits behind the label.
- Fix: Sky.tsx label colour #CFEBFF.
- Prevention: after replacing any background or hero art, re-check every label that overlaps it on the grid sheet. Automating this (a local contrast check under text boxes) is in BACKLOG.
- Status: fixed
### L-9 · 2026-11-25 · Elevator · minor
- Problem: the final "crane struck out" state was readable for only 1.42 s before the loop.
- Root cause: the strike started 2 frames after "not a crane" and took 10 frames; the narration ends close to the file end.
- Fix: the strike starts on "not" and takes 8 frames (≈1.6 s held), and a 1.0 s narration tail was added (episodes/02-elevator/tail.txt).
- Prevention: endings need the payoff state fully on screen ≥ 1.5 s before LOOP_FRAMES. Not automated yet (BACKLOG).
- Status: fixed
### L-10 · 2026-11-25 · kit · minor
- Problem: @remotion/three renders failed with "Error creating WebGL context".
- Root cause: headless Chrome on the box has no GPU; the angle, swiftshader, egl and vulkan backends fail.
- Fix: remotion.config.ts `setChromiumOpenGlRenderer("swangle")`.
- Prevention: keep swangle in config. 3D shots cost about 3.4× render time (Sky 27 → 93 s), so use at most one 3D hero per episode.
- Status: fixed
### L-11 · 2026-11-25 · kit · minor
- Problem: QA outputs from v3 iteration 1 overwrote v2's qa/<Id>/report_it1.* (restored from the original folder).
- Root cause: qa.py wrote to qa/<Id>/ regardless of render suffix.
- Fix: qa.py writes to qa/<Id>/<suffix>/ for any suffix other than v2 (`SUF` env var; iterate.sh passes it through).
- Prevention: every versioned output path includes the version suffix.
- Status: fixed
### L-12 · 2026-11-25 · kit · minor
- Problem: caption words with end < start (e.g. "An" 0.24/0.14).
- Root cause: whisper token timestamps; captions.py did not clamp them.
- Fix: captions.py sets end = min(max(end, start+0.08), next start).
- Prevention: the clamp lives in captions.py. A lint for monotonic timings is in BACKLOG.
- Status: fixed

## Round 4 entries
### L-13 · 2026-11-25 · kit · major (regression of L-8)
- Problem: labels under 4.5:1 WCAG contrast that a human review let through: Elevator "A CRANE" 2.3:1 (red label inside a panel faded to 55%), QR "NO SCAN" 2.9:1 (white on red pill), QR "→" glyph 2.4:1, Sky "SHORT PATH THROUGH AIR" 3.3:1 (white on blue pill).
- Root cause: colours were picked by eye per label; parent-group opacity (dimming a "loser" panel) also dims its label; white on saturated mid-tone pills is below 4.5:1.
- Fix: Elevator.tsx keeps the "A CRANE" label out of the dimmed group (full-opacity red on ink2); QR NO SCAN and Sky SHORT PATH pills use ink text; "→" replaced by ":" text.
- Prevention: automated. `scripts/contrast.py` (called by qa.py, check "labels: WCAG contrast >= 4.5:1 (held >= 0.6 s)") renders a probe pass where every Label/Pill text is pure magenta without outline (`--props {"probe":true}`, brand/Kit.tsx `PROBE`), measures the real background ring and the final MP4 text colour. Rule: never dim a label with its panel; dim the art only. On saturated pills use ink text.
- Status: fixed (verified 11/11 QA pass on QR_v4, Elevator_v4, Sky_v4)
### L-14 · 2026-11-25 · Elevator · major (from BACKLOG)
- Problem: Elevator frame 0 was dark (4% of stage pixels bright vs 28-57% on the others), so the thumbnail/first impression was weak.
- Root cause: the hook frame was the dark machine-room rig; qa.py only required 2% bright pixels at 0.3 s.
- Fix: v4 hook design (style frames) opens on a bright, paper-coloured shaft with the title-as-hook. Animation pending owner approval of the look.
- Prevention: qa.py "hook: frame 0 bright (>= 12% of stage pixels > 90/255) and at 0.3 s" (new automated gate; v3 Elevator fails it at 0.04).
- Status: fixed (Elevator_v4 frame 0 bright = 0.561, 0.3s = 0.555)
### L-15 · 2026-11-25 · kit · minor
- Problem: SFX onset density gate (1.0-1.8/s) let QR ship at 1.77/s and Elevator at 1.55/s, above the 1.2-1.5 target.
- Root cause: the gate was wider than the target ("within gate" was treated as done, L-6).
- Fix: qa.py now gates 1.2-1.5/s. v3 baseline: QR 1.77 FAIL, Elevator 1.55 FAIL, Sky 1.49 PASS.
- Prevention: gate = target. Trim order: micro-ticks first, then tick runs, then duplicate whooshes on camera moves.
- Status: fixed (QR_v4 1.32/s, Elevator_v4 1.27/s, Sky_v4 1.27/s)
### L-16 · 2026-11-25 · QR · major (new automated check)
- Problem: QR payoff state is never settled before the loop whip (0.07 s still; Elevator 1.53 s, Sky 3.03 s).
- Root cause: L-9's rule ("payoff complete >= 1.5 s before LOOP_FRAMES") was prose only; QR's ending keeps animating until the whip.
- Fix: QR.tsx Final: orbit blocks start at the "A QR code carries" line and settle in 14 frames; camera pull moved to the same frame (v4 it3: settled 3.17 s).
- Prevention: qa.py "end card: catchphrase card >= 1.0 s and payoff settled >= 1.5 s before loop" (stage ROI vs the last pre-whip frame, mean abs diff < 6/255).
- Status: fixed (QR 3.17 s, Elevator 1.70 s, Sky 4.03 s on v4)
### L-17 · 2026-11-25 · kit · minor
- Problem: the box is shared by several agents; scratch files in /tmp were overwritten by another agent during review (a preview strip showed someone else's frame).
- Root cause: generic /tmp names (q1.png, q3.png).
- Fix: round-4 scratch lives in /workspace/ttm-r4/_scratch.
- Prevention: never write review artefacts to /tmp with generic names; use the project folder.
- Status: fixed
### L-18 · 2026-11-25 · kit · minor
- Problem: photo licences from aggregators can differ from the source (Openverse items point at Commons pages with several licence links; a derivative file credits several authors).
- Root cause: trusting the aggregator's licence field / a landing-page regex.
- Fix: scripts/photos.py re-reads Commons items through the Commons API (by title or curid), rejects TIFF/WEBP/SVG deliveries unless a JPG/PNG rendition exists, and re-verifies at pick time.
- Prevention: skills/licensed-photos/SKILL.md; CREDITS.csv has a `verified_via` column.
- Status: fixed
### L-19 · 2026-11-25 · kit · minor (independent Gemini critic, all 3 episodes)
- Problem: the critic flagged secondary annotations as small on a phone: Elevator "≈ BALANCED" (0:03), QR "Reed-Solomon (1960)" (0:15), Sky "~1000× smaller than a light wave" (0:11).
- Root cause: qa.py had no lower bound on rendered text size; raw SVG <text> (CAR 26 px) bypasses <Label>.
- Fix: qa.py check "labels: minimum font size >= 30 px on all <Label> elements" (static scan of the episode .tsx). Raw <text> still open (BACKLOG).
- Prevention: repeated critic finding -> automated check. Extend the scan to raw <text>.
- Status: partly fixed (<Label> gated; raw <text> open)
### L-20 · 2026-11-25 · kit · minor
- Problem: the critic requested gemini-2.5-pro / 2.5-flash and both returned HTTP 404 ("no longer available to new users"); every v4 review silently ran on gemini-3-flash-preview.
- Root cause: model list hard-coded from older docs; the fallback logged only the exception type.
- Fix: critic.py records the model actually used in critic.json/critic.md and metrics.
- Prevention: check the models endpoint before a review round; report the model next to every score.
- Status: fixed (model recorded); default order to be updated in round 5
### L-21 · 2026-11-25 · kit · major
- Problem: the critic scored v3 Elevator 9.2/10, but the owner disliked v3 (and rejected both v4 style frames); v4 scored 9.3. The scores do not separate a rejected video from an approved one.
- Root cause: generic rubric with no anchored examples or references; scores asked for before weaknesses; a flash model.
- Fix (round 5): calibrated prompt (anchored mg-styles scale, Jared Owen/Animagraffs/The Why Side + the 7.6 Flat Vector contact sheet, hard caps, weaknesses before scores, weighted overall capped at weakest+2). Scores dropped from 9.2–9.3 to 5.9–6.5, but the absolute score STILL ranked rejected v3 (6.46) above approved v4 (6.06) on the same model. Pairwise `--compare` ranks them correctly in both orders (3-flash: v4 +1.55/+1.76 and −0.85 swapped; lite: +0.95 / −0.41 swapped). Ship decision = pairwise vs the last approved render.
- Prevention: a critic is only trusted after it ranks known-rejected below known-approved renders (done for pairwise, failed for absolute).
- Status: fixed for pairwise; absolute score kept only as a fix-list generator (L-22)

### L-22 · 2026-11-25 · kit · major (critic availability)
- Problem: gemini-3.1-pro-preview returned 429 on every call (free tier ~0); gemini-3.8-flash 503'd repeatedly, then both 3.8-flash and 3-flash-preview hit `GenerateRequestsPerDayPerProjectPerModel-FreeTier` = 20 requests/day. Round-5 calibration used the whole day's quota before v5 existed, so the v5 verdicts ran on gemini-3.1-flash-lite-preview.
- Root cause: the free tier is per-model/day; calibration samples (×2) + retries + compares burned it; the error message hid the quota id.
- Fix: critic.py prints the quotaId and retryDelay; transient retries skip 429s; `VIDEO_FPS` env option; lite validated on the known v3/v4 pair (correct in both orders, weaker margins).
- Prevention: budget ≤ 12 strong-model calls per round (3 compares + 3 calibrated + 3 verify + 3 spare); never calibrate and review on the same day without a paid key; lite is a fallback, not a judge for subtle diffs (it called QR v4 and v5 "identical" even at 5 fps).
- Status: open: strong-model v5 pairwise is pending the quota reset (`_scratch/critic_v5_strong.sh`)

### L-23 · 2026-11-25 · kit · minor (critic hallucinated defects)
- Problem: calibrated critics give loop 5/10 ("ending abrupt") on loops measured at seam PSNR 48 dB, and ask for entry animations on frame 0, which the hook gate requires to be bright and already on screen.
- Root cause: models sample about 1 fps and do not know the format; the FORMAT CONVENTIONS note is not enough for lite.
- Fix: `--qa-report` passes measurements; the routing rule ignores critic claims that contradict measurements (skills/critic).
- Status: mitigated

### L-24 · 2026-11-25 · QA · minor (probe renders current code)
- Problem: Sky it1 failed contrast at times where the MP4 was fine.
- Root cause: contrast.py renders a fresh probe from the CURRENT source; I edited Sky.tsx while the batch was still running QA, so the probe and the MP4 differed. Also TagLabel hid its backing in PROBE mode.
- Fix: TagLabel backing always drawn; never edit remotion/src while a QA batch runs (qa-loop skill).
- Status: fixed

### L-25 · 2026-11-25 · kit · minor (render cost)
- Problem: Sky it1 took 280 s to render (r4 124 s).
- Root cause: animated grain (4 full-frame PNG tiles alternating, +37 % per frame on a 150-frame benchmark) on top of the 3D planet.
- Fix: static grain tile by default (`{"grain":"anim"}` opt-in), FlatPlanet replaces Ortho3D Planet → Sky 62 s (−50 % vs r4).
- Status: fixed

### L-26 · 2026-11-25 · all · major (new gates found real defects)
- Problem: the new r5 gates failed v4-quality code: labels in the Shorts UI zones (ProofCard credit, QR REPAIR/REBUILDABLE, TitleHook fling, Sky 4.4×, Rayleigh formula under a punch), 4.0–4.6 s gaps with no visual state change, Sky ISS photo held 2.2 s, and only ~−37 dB of "silence" before the catchphrase (the riser ran into the card).
- Root cause: none of these were measured before; camera punches push edge text into the button column.
- Fix: safe-zone check in contrast.py/qa.py, cadence check (6d), silence-beat check (6e) + bed duck in mix_one.sh + riser at at−47; punches added at the gaps; text moved, made smaller, or punch offset changed; a mid-photo pill.
- Prevention: when you add a camera punch, re-check edge labels under the zoom: x' = 540 + s·(x−540) + dx must stay ≤ 900.
- Status: fixed (all 3 v5 PASS)

### L-27 · 2026-11-25 · facts · minor (fact gate false positive)
- Problem: facts.py blocked Sky on "two places" (a quantity word with no fact).
- Root cause: the number/quantity scan counts any number word, including rhetorical ones.
- Fix: mapped to f-0004 (noon vs sunset observers) instead of loosening the scan.
- Status: fixed. Keep the scan strict; map rhetorical numbers to the fact they describe.

### L-28 · 2026-11-25 · 05-anc · minor
- Problem: beat check failed (-34.8 dBFS before the catchphrase) and safe-zone/contrast checks failed on the first full render (title fling under a punch, 17-char label in x>900, red text on a 82% ink TagLabel over a light panel = 2.4:1).
- Root cause: tail of the riser plus my own clank + glide-swish cues landed inside the 0.2 s window; TagLabel backing width is estimated (0.6 em/glyph) and is too narrow for caps over light panels.
- Fix: removed clank/glide-swish cues in the last 1.5 s before the card, title fades before the punch, labels moved to x<=900, light-panel labels use paper text on the ink tag.
- Prevention: on light panels use TagLabel with paper text only; keep camera swishes out of the 1.5 s before "That's the mechanism". Checked by qa.py (beat, contrast, safe zones).
- Status: fixed (15/15 on ANC v6 it3)
### L-29 · 2026-11-25 · env · minor
- Problem: `npx remotion render` crashed (Cannot find module @babel/core/lib/tools/build-external-helpers.js) in ttm-r6.
- Root cause: incomplete node_modules install (only the CLI path needs it; the node API used by storyboard.py worked).
- Fix: restored the missing lib/tools folder from the identical @babel/core 7.29.13 in a sibling checkout.
- Status: fixed locally

### L-30 · 2026-11-26 · r6 · major
- Problem: the critic found defects every existing gate passed: an icon hiding the `CHIP` label (ANC_v6, 16 s), a label pushed off the left edge (Elevator_v6, 17–26 s), and flat-popping badges.
- Root cause: gates measured contrast and safe zones but not geometry between elements or distance to the frame edge, and not entrance motion.
- Fix: added A13 (icon/label clearance ≥ 36 px), A14 (badge pop with anticipation/overshoot) and A15 (text ≥ 24 px from the side edges), plus `Lane` / `LabeledBox` / `TagLabel` components in `Kit.tsx`.
- Prevention: critic findings that are measurable are promoted to gates by `scripts/lessons.py` output (`docs/STYLE_RULES.md`, candidate gates). Open gaps are listed in `docs/ROUND6.md`.
- Status: fixed for A13–A15; gaps in ROUND6.md remain.

### L-31 · 2026-11-26 · setup (macOS) · major (pipeline did not run on a fresh Mac)
- Problem: on a fresh macOS box, `scripts/setup.sh` failed (`onnxruntime` has no wheel for Homebrew's default Python 3.15). `new-episode.sh` used GNU `sed -i` with a `\n` replacement, which fails on BSD sed. `metrics.py` read `/proc`, which crashed every timed stage, and `build-episode.sh` (`set -e`) aborted after TTS. `contrast.py` used `-vsync 0`, which FFmpeg 9 removed, so the WCAG/safe-zone gate errored without measuring anything. `master.sh` needed `tools/fn-venv`, which setup never created.
- Root cause: the scripts had only been run on Linux with older FFmpeg/Python.
- Fix: venv built with python3.12. new-episode.sh edits Root.tsx with Python (portable). metrics.py has a `ps` fallback when there is no /proc. contrast.py uses `-fps_mode passthrough`. setup.sh installs ffmpeg-normalize into tools/fn-venv.
- Prevention (code): setup.sh picks python3.12/3.13 and refuses >= 3.14 with a clear message; scripts/check_portability.py (run by iterate.sh and build-episode.sh before rendering) fails on -vsync, GNU `sed -i "..."` and absolute paths. Treat a gate that *errors* as a tooling bug, not a design FAIL.
- Status: fixed

### L-32 · 2026-11-26 · Microwave · minor (hold after the hook zoom)
- Problem: Microwave it1 had a 2.4 s stage hold at 0.97–3.4 s: the scale reveal ends at 1.0 s and the next visual event came at "So why" (3.2 s). Mug rotation and steam were too small to count as motion.
- Root cause: the hook had a single reveal and no secondary motion that the motion metric can see.
- Fix: a slow camera push from 1.0 to 2.7 s, and the microwave rings faintly visible from frame 0 (full strength on "So why").
- Prevention: qa.py motion gate (already present). In the storyboard, check the gap between the end of the hook reveal and the first spoken beat.
- Status: fixed in it2 (pending QA)

### L-33 · 2026-11-26 · Microwave · major (critic round 1, Antigravity gemini-4-neon-high, it3 = 5.06)
- Problem: (a) "SEES A WALL" was drawn over "MICROWAVE · ≈ 12 cm" at 0:38; (b) "ONE HOLE" was on screen for < 0.5 s before the whip; (c) light rays (±9 px) crossed the screen bars instead of passing through the 14 px gaps, which contradicts the narration; (d) "METAL SCREEN" sat on top of the holes; (e) the leakage-limit oven was a featureless slab.
- Root cause: two TagLabels shared one anchor; the hole pop was timed to the last word of its shot; wave amplitude was not checked against the gap size; the side-view oven had no identifying details.
- Fix (it4): the label slot is handed over (MICROWAVE fades as MICROWAVE SEES A WALL arrives); the hole appears at "twelve" (+1.5 s on screen); bars 34 px, gaps 20 px, light amplitude 4 px; METAL SCREEN moved above the plate; the oven gets a body shadow, vents, feet, door seam and handle.
- Rejected critic claims (contradicted by measurements): broken loop seam (PSNR 48.5 dB), holds > 2 s (longest 1.27 s), labels < 30 px (both font gates pass).
- Prevention: label collisions are not gated yet. The probe render already knows every Label/TagLabel box, so contrast.py could flag overlapping boxes held >= 0.6 s (BACKLOG, gate). Rule (prose until gated): a wave drawn "through a hole" has amplitude + stroke/2 < gap/2.
- Status: fixed in it4 (pending QA + verify)

### L-34 · 2026-11-26 · env · major (r6 scripts pinned to one machine)
- Problem: on the Mac, after merging round 6, `iterate.sh` rendered fine but QA never ran: `scripts/metrics.py ... scripts/qa.py` failed with "No such file or directory" although qa.py existed.
- Root cause: round 6 changed the shebang of `scripts/qa.py` and `scripts/critic.py` to `#!/workspace/ttm-r6/.venv-tts/bin/python` (the other box's venv). The exec fails when the interpreter path is missing, and Python reports the script itself as missing.
- Fix: both back to `#!/usr/bin/env python3`; the pipeline puts `.venv-tts/bin` first on PATH.
- Prevention (gate): scripts/check_portability.py fails on any shebang other than `/usr/bin/env python3|bash|sh|node` or `/bin/(ba)sh` and on `/workspace/` paths; iterate.sh and build-episode.sh run it before rendering.
- Status: fixed

### L-35 · 2026-11-26 · QA · minor (iterate.sh judged a stale MP4; A13 glyph split)
- Problem: (a) it6's first render timed out fetching Google Fonts; iterate.sh then mastered and QA'd the previous MP4 as if it were it6. (b) A13 reported "5 mW/cm²" (JetBrains Mono 104 px) as two boxes 12 px apart: the monospace superscript sits centred in a wide cell.
- Fix: iterate.sh stops (continue) when render.sh fails. The episode number uses the proportional display font.
- Prevention: (a) is now code. (b) BACKLOG: contrast.py occupancy could merge magenta components that come from one Label (probe id per label) instead of relying on 2 px dilation.
- Status: fixed

### L-36 · 2026-11-26 · r6 tooling · major (lessons.py wiped the rule base on a second machine)
- Problem: `ship_check.sh` ends with `scripts/lessons.py`. On the Mac it rewrote docs/STYLE_RULES.md, style_rules.json and active_rules_prompt.txt from only the Microwave critic files. The 5 active prose rules from QR/Elevator/Sky/ANC disappeared ("no active prose rules yet").
- Root cause: lessons.py rebuilds from the critic JSONs under qa/**, and those are gitignored (only `critic.json` is kept), so a fresh clone has none of the other episodes' `general_rules`.
- Fix: restored the three files from git. The Microwave general_rules are still in qa/Microwave/v1/ship_it8/critic_cal.json, waiting to be merged.
- Prevention (gate): lessons.py `guard_active()` exits 3 and writes nothing when a rebuild would drop a rule that is active in the committed docs/style_rules.json (`--force` to override). Tested on this Mac: refused to drop 23 active rules. Open: true incremental merge (BACKLOG).
- Status: fixed (guard); incremental merge open

### L-37 · 2026-11-26 · r10 security · major (agents ran with permission checks bypassed)
- Problem: scripts/llm.py started every write role with `claude --dangerously-skip-permissions`, every agy role with `--dangerously-skip-permissions` (plus `--force` for cursor-agent writes), with the full parent environment (other API keys) and with critic/QA text pasted into the prompt as plain instructions. A prompt injection in a critic finding or generated rule could run any command on the machine.
- Root cause: headless agents had no other way to edit files without prompting, and the only guard was the post-hoc scope revert.
- Fix (code): claude write roles use `--permission-mode acceptEdits` + an explicit `--allowedTools` list (Read/Glob/Grep/Edit/Write + `npx tsc --noEmit`, `scripts/preview.py`, `scripts/lint_shots.py`) and `--disallowedTools` for web/agent tools; read-only roles get read tools only; agy runs `--sandbox --mode plan|accept-edits`; cursor-agent write roles are refused (no allowlist); `child_env()` strips *KEY/TOKEN/SECRET/PASSWORD/CREDENTIAL* vars except the provider's own login; `llm.untrusted()` wraps QA/critic text. SUF reaches agents via the environment, so no `VAR=... cmd` allow rule is needed. Real-CLI smoke test: agy (plan+sandbox) and claude (allowlist) both answered.
- Prevention (gate + test): scripts/check_portability.py fails on `dangerously-skip-permissions`, `bypassPermissions` and `"--force"` agent args (runs before every render); tests/test_llm_security.py checks the argv/env of every provider and role. tests/test_r7_pipeline.py no longer asserts the bypass.
- Follow-up (same day, automated security review of the r10 commit): (1) an allowlisted command runs repo code (scripts/preview.py), so an unscoped Edit let the builder rewrite that script and then run it; (2) a secret *name* denylist misses DATABASE_URL-style secrets. Fixed: Edit is path-scoped to the role's scope globs and scripts/, prompts/, tests/, .venv-tts/, node_modules, package/tsconfig, brand kit, Root.tsx, config and docs are Edit-denied; agy/codex/cursor-agent (no path-scoped edits) serve read-only roles only; the agent env is an allowlist (PATH/HOME/locale/SUF + the provider's own login). Real-CLI proof: asked to append to scripts/preview.py, Claude answered DENIED and the file hash did not change (blocked by permission, not reverted afterwards). tests/test_llm_security.py: 8 cases, incl. t_allowed_commands_cannot_be_edited.
- Follow-up 2 (second automated review): `--permission-mode acceptEdits` auto-approves every edit inside the project, so the Edit(scope) allow rules restricted nothing and only the denylist held; my real-CLI test had only probed a DENIED path. Fixed: write roles use `--permission-mode default` (in -p, anything outside --allowedTools is denied); PROTECTED also covers CLAUDE.md, GEMINI.md, .mcp.json, **/.npmrc, **/.env*, remotion/src/index.ts. Real-CLI proof with three cases: in-scope Microwave.tsx edit DONE; out-of-scope, unprotected remotion/src/index.ts DENIED; protected scripts/preview.py DENIED; reverted=[] in all three (denied at permission time).
- Prevention: a permission test must probe an allowed path, an unlisted path and a denied path, not only the denied one.
- Status: fixed

### L-38 · 2026-11-26 · r10 efficiency · major (parallelism made the pipeline slower; measure first)
- Problem: the r10 "prefetch" ran the main render (concurrency 10), two stem renders and the contrast/occupancy probe pass at once. On the 15-core M5 Pro that is ~29 browser workers: the main render took 886 s instead of 235 s, the two simultaneous `remotion render` stem processes both failed, and QA crashed. Total 1247 s vs 898 s before.
- Root cause: optimising without a profile. The new per-check timing (qa.py `res["timing"]`) showed the real split of the 663 s QA: SFX/voice stem renders 317 s + contrast/occupancy probe renders 315 s; all MP4 analyzers together 18 s.
- Fix: prefetch and parallel stem renders removed; concurrency back to 6 (RENDER_CONCURRENCY / PROBE_CONCURRENCY env overrides). The voice stem is now copied from remotion/public/<slug>.wav, measured bit-identical (diff -240 dB): one full render fewer per QA. Verified: same 37 verdicts on the same MP4 (24 PASS / 13 FAIL). Kept: per-check timing, fail-fast static gates, parallel MP4 analyzers (small), parallel agy calls in ship_check.
- Measured on AC power (2026-11-26, Microwave, render concurrency 6, pre-r10 code in a worktree at 32dd35b vs HEAD a7c9e30, one run at a time): OLD render 244 s + QA 570 s = 814 s; NEW 241 s + 398 s = 639 s and 235 s + 400 s = 635 s (run-to-run spread about 1 %). QA -30 %, full iteration -22 % (~3 min saved), identical verdicts in all three runs (24/37). The battery runs earlier were 15-40 % slower and noisy: never benchmark on battery.
- Next targets (NEW per-check timing): contrast/occupancy probe pass ~210 s, the single SFX stem render ~172 s; everything else ~7 s.
- Prevention: optimise from `report_itN.json` timing; never run two `remotion render` processes on the same project at once (comment in qa.py).
- Status: fixed (measured)

### L-39 · 2026-11-26 · r10 learning loop · major (critic output did not turn into work)
- Problem: the critic returns a score, timestamped weaknesses with fixes, and 4-8 reusable general_rules, but (1) build_loop.py stopped at "judge": the episode's weaknesses stayed in critic_cal.md until someone applied them by hand (the Microwave pilot); (2) 10 active, measurable rules were classified candidate_gate: not in code and, because only prose rules reach the prompt, not in the builder prompt either; (3) "already enforced" was decided by keyword match and never checked against what the gate measured.
- Fix (code): build_loop.py `polish` step: after a SHIP that the calibrated critic still marks ONE MORE PASS, scripts/polish.py turns the blocker/major weaknesses into a builder task (wrapped as untrusted data; items a passing gate measured as OK are flagged "confirm on the stills first"), and the result goes back through preview -> ship -> judge against the ACCEPTED render; a polish that loses is reverted (TSX + MP4 + report). loop.max_polish_rounds = 1. critic.py records `qa_report`; lessons.py marks `gate_miss` when the critic reports a rule on a render whose matching gate PASSED; active candidate gates and gate misses ride in docs/active_rules_prompt.txt as interim rules; docs/gate_backlog.json lists them (misses first, by severity) with the evidence a new gate must fail on. `lessons.py --refresh` regenerates prompt + backlog from the committed rule base (10 interim rules active now).
- Prevention (tests): tests/test_r10_learning.py, 6 cases, incl. an end-to-end build_loop simulation (renders, QA, critic and LLM faked) for a losing polish (reverted) and a winning one (kept, one round max).
- Open: gatesmith role (backlog -> gate + test, promoted only if it fails the evidence render and passes an approved one).
- Status: fixed (polish, gate_miss, interim rules, backlog); gatesmith open
