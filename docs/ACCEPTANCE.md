# Acceptance checklist (every episode, every iteration)

Run: `scripts/iterate.sh <N> <Id>` (lint → render → QA, all timed into metrics/) then review the sheets it prints.
An episode ships only when every automated check PASSes **and** the visual review finds no style failure.

## Automated (scripts/qa.py → qa/<Id>/report_it<N>.json)
| # | Check | Threshold | How |
|---|-------|-----------|-----|
| A1 | Format | 1080x1920, 30 fps, H.264 + AAC 48 kHz, 35–55 s | ffprobe |
| A2 | Loudness | integrated −15.5…−13 LUFS, true peak ≤ −1 dBTP | ffmpeg ebur128 |
| A3 | SFX under voice | median SFX peak 10–16 dB under the voice (400 ms RMS), none closer than 8 dB | stems rendered with `--props '{"stem":"sfx"}'` / `"voice"` |
| A3b | SFX density | 1.2–1.5 SFX onsets/s (gate = target since round 4); onset = 50 ms window rising >6 dB, above −55 dBFS, ≥80 ms apart | sfx stem (round 3) |
| A4 | Motion every 1–2 s | no stage hold > 2.0 s (0.2 s-window frame diff on y 290–1190 below 0.5) | ffmpeg rawvideo + numpy |
| A5 | Hook visual in the first second | subject drawn at 0.3 s and visible change by 1.0 s | stage ROI |
| A6 | Exact loop | seam jump (last→first frame) ≤ p95 of normal frame steps, PSNR ≥ 25 dB | full frame |
| A7 | Storyboard lint | phrases resolve, no fades, ≤8 words per on-screen text, no 3 pushes in a row, beat every ≤3 s, first beat <1 s | scripts/lint_shots.py |

## Visual review (reviewer, using transitions_it<N>.png = 8 frames around every shot boundary and the loop seam, grid_it<N>.png = 1 frame / 1.5 s)
| # | Check |
|---|-------|
| V1 | No overlaps: brand chip/tag (y<290), stage, captions (y 1222–1440), deck (1462–1552); nothing important in x>900 below y 900 or y>1560 |
| V2 | Captions readable: 84 px, ≤3 words/page feel, active word amber, never on top of bright art |
| V3 | SFX in sync: every cue lands on a visible event (whoosh = transition, pop = label/pill, tick = counter/element, riser → card, sting = catchphrase) |
| V4 | Transitions are world moves (push-through / whip / whipUp / cut+punch) — no cross-fades between sections |
| V5 | ≤2 text levels on the stage (LABEL ≥30 px + verdict pill); text never clipped by the camera |

## Style failures (render → look → fix list; claude-drawing-skill style)
- **Slideshow**: a section is a static card with text fading in → give it a persistent subject + camera beat.
- **Empty half**: art crowded into one half of the stage while the other half is empty.
- **Camera into UI**: a punch/glide pushes art or text under the brand tag, into captions or off-screen. Verdict pills go in the Shot `hud` (screen space).
- **Clipped label**: camera crops a label mid-word.
- **Edge objects**: art in the right-hand platform column (x>900, y>900).
- **Triple push**: same camera move three times in a row → monotone.
- **Late hook**: first meaningful change after 1 s, or a title card first.
- **Dead air**: >2 s with nothing moving on the stage.
- **SFX spam**: SFX closer than 8 dB to the voice or more than ~2 per second.
- **Double meaning colour**: red/green used for anything other than fail/success.

## Round 4 automated gates (scripts/qa.py)
- A8 SFX onset density **1.2-1.5 /s** (was 1.0-1.8).
- A9 Labels (Label + Pill text) WCAG contrast >= 4.5:1, failing only if held >= 0.6 s (scripts/contrast.py, probe render). Outputs contrast.json and contrast_fail.png.
- A10 End card: "That's the mechanism" card >= 1.0 s, payoff state settled >= 1.5 s before the loop whip.
- A11 Hook: frame 0 and 0.3 s have >= 12% bright stage pixels (> 90/255).
- Photos: every on-screen photo has a CREDITS.csv row with a PD/CC0 licence verified at the source (skills/licensed-photos).
- A12 Labels: every `<Label size>` in the episode .tsx is >= 30 px (static scan; raw SVG `<text>` is the next step).
- A13 Labels: no two stage label/pill occupancies closer than 36 px, and no icon covering a pill interior, held >= 0.6 s (`scripts/contrast.py` overlap; evidence `overlap_fail.png`). Prefer `Lane` / `LabeledBox` so the layout cannot collide.
- A14 Motion: badge/pill entrances (TagLabel, Pill, TitleHook backings) pop with anticipation/overshoot, never snap in at full size (`scripts/contrast.py` occupancy pass). r7: hand-rolled badges (text on a compact uniform non-cyan backing) are tracked too; byte/table grids (>= 3 same-size cells on a row) are excluded.
- A9b (r7) Contrast also covers raw SVG `<text>` drawn by an episode: on the probe passes `EpisodeShell` paints stage `svg text` magenta, so WCAG, safe-zone, clearance and clutter gates see it.
- A15 Labels: text stays inside the Shorts UI safe zones and >= 24 px from the left/right frame edge, held >= 0.6 s (`scripts/contrast.py` `unsafe()`, EDGE=24). r7: in the first 2.0 s (hook/intro) every sampled frame counts, so a sub-0.6 s clip at the hook fails. After any camera punch/push, re-check edge labels.
- A16 (r7) Framing: no whole-stage card (one closed box covering >= 55 % of the stage band) held >= 1.0 s, and boxed framing (closed box >= 30 %) <= 50 % of the runtime (`scripts/framing.py`, MP4 or stills). The chapter deck and captions are outside the stage band; the outro card window is excluded.
- A17 (r7) Layout: no more than 3 pill-shaped callouts (TagLabel/Pill backings + hand-rolled badges; h <= 120 px, w >= 1.6 h) on the stage at once, held >= 0.6 s (`scripts/contrast.py` clutter).
- A18 (r7) Text: no decorative HUD / fake timecode strings in the episode source (`scripts/static_gates.py`: `00:12`, `REC`, `T+3`, `60 FPS`, `ISO 100`, `HUD`). The real chapter deck lives in `brand/Chrome.tsx` and is not scanned.
- Preview (r7): `scripts/preview.py` runs A9, A9b, A12–A18, the hook and loop (frame 0 vs last) checks and approximate hold/cadence on stills, with no full render. Audio, loudness, SFX, end-card and exact motion gates run only on the shipped render (`scripts/qa.py`).
- A19 Pipeline: `scripts/check_portability.py` passes before any render (no absolute shebangs or `/workspace/` paths, no ffmpeg `-vsync`, no GNU-only `sed -i "..."`); `iterate.sh` / `build-episode.sh` stop on failure (L-31, L-34).
- A20 (r10) Captions: consecutive caption words keep a visible gap and no 1-2 character word sits alone on the last line (`scripts/caption_spacing.py`, OCR on the caption band at 5 fps). First gate written by the gatesmith role (gates_candidate/R-045), validated FAIL on Microwave it8 / PASS on it15, promoted by Felipe. Component: brand/Chrome.tsx Captions (0.22em gap, textWrap balance).

## Independent critic (round 4, advisory)
After all automated checks pass, run `scripts/critic.py <Id>` (needs `GEMINI_API_KEY` in the environment). It uploads the MP4 with audio to Gemini and writes `qa/<Id>/<SUF>/critic.json` + `critic.md` (8 scores 1–10, timestamped issues, suggestions). The builder never grades its own work: route findings to `docs/LESSONS.md` / `docs/BACKLOG.md`; a finding that repeats becomes a qa.py check. Any score < 7 means one more iteration. The critic is not yet calibrated (L-21): it is a second opinion, not the gate.

## Style-frames gate (round 4)
Before animating a new look, render stills for each candidate look (`remotion/style_frames.mjs`, `scripts/style_sheet.py` → `style_frames/`) and get the owner's pick. Animation starts only after the look is approved.
