# Acceptance checklist (every episode, every iteration)

Run: `scripts/iterate.sh <N> <Id>` (lint → render → QA, all timed into metrics/) then review the sheets it prints.
An episode ships only when every automated check PASSes **and** the visual review finds no style failure.

## Automated (scripts/qa.py → qa/<Id>/report_it<N>.json)
| # | Check | Threshold | How |
|---|-------|-----------|-----|
| A1 | Format | 1080x1920, 30 fps, H.264 + AAC 48 kHz, 35–55 s | ffprobe |
| A2 | Loudness | integrated −15.5…−13 LUFS, true peak ≤ −1 dBTP | ffmpeg ebur128 |
| A3 | SFX under voice | median SFX peak 10–16 dB under the voice (400 ms RMS), none closer than 8 dB | stems rendered with `--props '{"stem":"sfx"}'` / `"voice"` |
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
