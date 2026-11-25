# Improvement backlog
Ideas and suggestions from reviews that are not bugs. Reviewers append; whoever implements one moves it to Done with the commit.

## Open
- [ ] Extend `qa.py` minimum font-size gate from `<Label>` (>= 30 px) to raw SVG `<text>` elements (e.g. `CAR`, `EMPTY CAR`) so mobile readability matches primary labels (from critic L-17).
- [ ] (r4 critic) Give `ProofCard` a softer eased slide/scale entry (`Sky` 0:32) and slightly more breathing room below the top `BrandChip` (`QR` 0:38), plus a subtle brightness/contrast boost on the archival HABS motor photo (`Elevator` 0:35).
- [ ] (r4 critic) Add a subtle spring-buffer compression thud SFX in `Elevator` when the car approaches pit buffers.
- [ ] Voice: owner listens to voice_ab/compare/*.wav. Qwen3-TTS was tested in round 3 and not adopted (slow, not clearly better). Kokoro am_fenrir has the widest pitch range (12.7 st vs 8.6 for michael), so it is worth a human listen. An owner voice clone is still untested.

- [ ] Caption timing lint: monotonic start/end per word (from L-12).
- [ ] explainroo ideas: a picture change at least every 2 s (lint is ≤3 s today); `{shown|spoken}` pronunciation overrides in tts.py; a second hook mid-video.
- [ ] Speed up the 3D hero render (Sky 93 s): render the planet as a pre-rendered image sequence once, or lower the icosahedron detail.
- [ ] d2 as a storyboard/planning aid (static diagrams, not for on-screen use).

- [ ] (r4) Re-record the first line of each script as a title hook ("This is the elevator that barely lifts you." etc.) once the voice clone arrives; for now Kokoro am_michael.
- [ ] (r4) Replace the 3D planet with the flat 2D `earth_flat` in Sky (style frames use 2D): saves ~3x render time (L-10) and matches the flat look.
- [ ] (r4) QR episode shows a real scannable QR (qr-matrix.json -> youtube.com/@thatsthemechanism). Confirm the owner controls that handle before publishing, or switch to the non-scannable `qr_generic`.
- [ ] (r4) Contrast probe for raw SVG <text> (CAR, MOTOR, CW) and for the credit line; today only Label/Pill are probed.
- [ ] (r4) Lottie: animate the brand chip gear and the "STILL SCANS" check with library Lottie files (gear_spin, check_pop).
- [ ] (r4) drawing-skill backdrops as 2-3 parallax plates (far/mid/near) instead of one flat JPG, so ShotLayers can move them.
- [ ] (r4) LOC API timed out (30 s) on every search; add retry/backoff or drop it from defaults.

## Done
- [x] Independent multimodal VLM video+audio critic (`scripts/critic.py` + `skills/critic/SKILL.md` via Gemini Files API, $0 free tier, logged to `metrics/runs.jsonl` and `qa/<Id>/v4/critic.{json,md}`). (round 4)
- [x] Trim QR SFX onset density into the strict 1.2–1.5/s gate (`1.32/s` on `QR_v4.mp4`, `1.27/s` on `Elevator_v4` and `Sky_v4`). (round 4)
- [x] Owner look selection + v4 animation pass: Look A + `claude-drawing-skill` backdrops (`QR`, `Sky`) + upgraded mechanical Look A (`Elevator`), `TitleHook` scale reveals, and public-domain/CC0 `ProofCard`s. (round 4)
- [x] Automated contrast check (from L-8). (round 4: scripts/contrast.py probe render + WCAG gate in qa.py)
- [x] Automated ending check (from L-9). (round 4: qa.py end-card gate)
- [x] Elevator hook brightness gate. (round 4: qa.py frame-0 >= 12% bright; design fixed in style frames)
- [x] Raise SFX density toward ~1.2-1.5/s without clutter (v2 measured ~0.5/s). (round 3: 1.49–1.77/s measured by qa.py onsets; papercut SFX + camera cues + micro-ticks)
- [x] Elevator ending: make "scale vs crane" bigger and readable >= 1.5 s before loop. (round 3: full-width two-panel ending, ≈1.6 s fully struck before loop)
- [x] Add depth: parallax, shadows, light isometric or one @remotion/three hero shot. (round 3: ShotLayers parallax/shadow, iso extrusions, 3D planet in Sky)
- [x] Two-pass loudness with ffmpeg-normalize. (round 3: scripts/master.sh, −14.0 LUFS on all 3)
- [x] Lucide icons for labels. (round 3: Pill icon prop; QR + Elevator)
