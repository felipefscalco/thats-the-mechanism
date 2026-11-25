---
name: critic
description: Independent multimodal video critic via Gemini Files API (watches the rendered MP4 with audio). Use after automated QA passes; pairwise against the last owner-approved render decides ship/no-ship.
---
# Independent Video Critic (round 5: calibrated)

The builder never grades its own work (motion-video-kit Gauntlet). `scripts/critic.py` uploads MP4s to Gemini (Files API, key only in the
`x-goog-api-key` header from `GEMINI_API_KEY`; never print it) and writes `<name>.json` + `<name>.md`, logging model, tokens and $0 to metrics.

## Modes
- `--compare A.mp4 --mp4 B.mp4` **(the decision mode)**: pairwise, weaknesses of A and B first, per-dimension winner + margin 0-3, overall preference.
  A = the last render the owner approved (e.g. `Elevator_v4.mp4`), B = the candidate. Ship only if B is preferred. Run the swap (A↔B) once per round to catch position bias.
- default `--mode calibrated`: anchored mg-styles scale (5 student · 6 template · 7 pro · 8 agency · 9 award), reference channels
  (Jared Owen, Animagraffs, The Why Side, mg-styles-15 Flat Vector contact sheet attached), hard caps, channel format conventions,
  weaknesses BEFORE scores, overall = weighted mean capped at weakest+2. Use for the fix list, not for ranking (see L-22).
- `--verify prev.json`: fresh critic marks each previous item FIXED / PARTLY / STILL PRESENT (Gauntlet verification round).
- `--qa-report qa/<Id>/<suf>/report_itN.json`: hands measured numbers to the critic (authoritative over impressions).
- `--samples N` averages N calls. `--mode legacy` = round-4 prompt (kept only for before/after comparisons).

## Models
Default order `gemini-3.1-pro-preview` (free tier: 429 every time so far) → `gemini-3.8-flash` (frequent 503) → `gemini-3-flash-preview`.
Transient 503/disconnects retry once; the model actually used is recorded per file and a warning is printed if it changes between samples.
Compare scores only within one model.

## Routing
1. `scripts/ledger.py add <Id> --round N --artifact ... --critic ... --changes ... --measured ...` (qa/<Id>/gauntlet.md).
2. Fix the largest gap first; repeated findings become qa.py checks; bugs → docs/LESSONS.md, ideas → docs/BACKLOG.md.
3. Ignore critic claims contradicted by measurements (e.g. "loop cuts abruptly" when the seam PSNR is 48 dB).
