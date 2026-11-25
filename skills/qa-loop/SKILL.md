---
name: qa-loop
description: Render a Short and iterate until it passes automated QA and a visual review against the acceptance checklist. Use when rendering, reviewing frames, fixing QA failures, or deciding whether an episode is done.
---

# qa-loop

An episode is not done when it first renders. It is done when every automated check PASSes **and** a visual review finds no style failure. Checklist: `docs/ACCEPTANCE.md`.

## Commands

```bash
# First full run (TTS → captions → mix → lint → tsc → render → QA), all timed:
scripts/build-episode.sh <slug> <CompId>

# After animation or shot-table edits (iteration N = 2, 3, …):
scripts/iterate.sh <N> <CompId>

# Typecheck only:
(cd remotion && npx tsc --noEmit -p .)
```

Outputs:

- `renders/<CompId>_v2.mp4` (gitignored)
- `qa/<CompId>/report_it<N>.json`
- `qa/<CompId>/grid_it<N>.png` — one frame every 1.5 s
- `qa/<CompId>/transitions_it<N>.png` — eight frames around every shot boundary and the loop seam

Metrics append to `metrics/runs.jsonl`; summaries regenerate in `metrics/metrics.json` and `docs/METRICS.md`.

## Automated checks (must all PASS)

A1 format (1080×1920, 30 fps, H.264+AAC, 35–55 s) · A2 loudness · A3 SFX under voice · A4 motion every 1–2 s · A5 hook visual in the first second · A6 exact loop (seam PSNR ≥ 25 dB) · A7 storyboard lint.

## Visual review (you must actually look)

Open the grid and transition sheets (and sample frames of the MP4 if needed). Fail the episode for: slideshow energy, empty half of the stage, camera pushing art into the brand chip / captions / off-screen, clipped labels, art in the platform column, three identical camera moves in a row, hook later than 1 s, dead air, SFX spam, or red/green used for anything other than fail/success.

This look-then-fix loop is intentional (same idea as claude-drawing-skill). Prefer a short, specific fix to a rewrite of the kit.

## Rules

- Do not declare the video “acceptable” from JSON alone.
- Do not publish. After PASS + a clean visual pass, go to `package-metadata` and wait for **human approval of the final video**.
- If you change `remotion/src/brand/`, re-QA every active episode, not just the one you were editing (the IceDemo loop bug was a kit defect).

## Log what you found
Before reviewing, read `docs/LESSONS.md`. After each iteration, append findings there (problem, root cause, fix, prevention, status) and ideas to `docs/BACKLOG.md`. Never fix something silently.
