# VIDEO — QR

**Goal.** In 52 seconds the viewer must understand that a QR code is built to survive damage. The encoder adds extra "repair bytes" calculated from the data. At level H that budget rebuilds about 30 % of the code, so a logo, glare or scratches are planned-for damage. The three big corner squares carry no data and are how the camera finds the code, so covering one ends the scan. They should feel the code is alive and repairs itself, then a sharp "it's over" at the finders. The one special moment (`hero@restore about 30%`) is a big centred QR whose punched-out modules are rebuilt on screen. Amber parity arcs reach into the gaps and repair-byte chips fly in and flip each module back. The QR is the real level-H code for youtube.com/@thatsthemechanism, and it actually scans. The look, shot order, camera grammar and palette of `QR.tsx` (render `QR_v6.mp4`) stay. This is a targeted revision, not a rebuild.

## Frozen script
This QR code repairs itself. Your camera reads a damaged code anyway.

When the code is generated, your link is cut into bytes, and the encoder adds extra bytes calculated from the data itself. That's Reed-Solomon error correction, the same math that kept scratched CDs playing.

Those extra bytes are a recipe for rebuilding whatever goes missing. At the highest level, H, a scanner can restore about thirty percent of the code's bytes.

So a logo in the middle is just damage the code was built to survive. In real tests, about fifteen percent of the area is safe. Glare and scratches spend the same budget.

But cover one of the three big corner squares, and it's over. Those aren't data. They're how your camera finds the code.

That's the mechanism. A QR code carries its own spare parts.

## Shots
Times come from `captions.json`. Every pop is timed to the caption word, never to a round number. Shot phrases in `shots.md` resolve against caption text, so spoken "thirty percent" is written `30%` there. The `Enter` / `Pop` timings below are in seconds and become `at(...)` calls in the code.

| # | Anchor phrase | Dur | Visual idea (one continuous world) | Camera | On-screen text (≤2 levels, ≤6 words) | Max callouts |
|---|---|---|---|---|---|---|
| 1 | `This QR code repairs itself` (0.2 → 5.34) | 5.1 s | Bright QR with centred spinning amber gear logo, filling the frame at frame 0. Frame 0 is already the subject. The scale reveal runs from detail to whole code. On "repairs" (1.40) three module patches blink out and on "itself." (1.88) snap back in as amber → ink: the code visibly repairs itself. The patches never touch the finders and the logo. From "Your camera" (2.54) a Viewfinder pops in white and turns green, and a green scan beam sweeps the QR continuously until the cut. | scale-reveal pull, push@Your camera, punch@anyway. | `THE CODE THAT REPAIRS ITSELF` (TitleHook, top, stays until 5.1 s); `LINK OPENS` pill @anyway. 4.62 | 2 |
| 2 | `When the code is generated` (5.34 → 19.22) | 13.9 s | One byte world, wide grid. Beat A, 5.4–7.7: the URL types out in mono and each typed character flies down as a hex byte chip into the data grid, one chip every 2 frames, with the cursor blinking. Beat B, "cut into bytes" (7.72): chips pop and run a slow tick sweep. Beat C, "adds extra bytes" (9.82): 12 amber repair chips drop into a second grid and flow arcs run data → repair. Beat D, "calculated" (11.22): arcs draw from the data row into the repair row, with no text yet. Beat E, "data" (11.88): the DATA tag and `= f(DATA)` pop together. Beat F, "Reed-Solomon" (13.74): the REED-SOLOMON label pops and a pulse travels the grids. Beat G, "scratched CDs" (17.44): a CD with a red scratch rotates in a card that replaces the REED label (binary swap), and `STILL PLAYING` pops. The grid is 6 × 2 chips 100 × 80 px, pitch 120, x 130–830, repair rows below. Nothing sits at x > 900 below y 900. | settle, punch@cut into bytes, glide@adds extra bytes, glide@Reed-Solomon, push@same math, pull@scratched CDs | `DATA` @data 11.88; `REPAIR BYTES` @adds extra bytes 9.82; `= f(DATA)` @data 11.88; `REED-SOLOMON (1960)` @Reed-Solomon 13.74; `STILL PLAYING` @scratched CDs 17.44 | 3 |
| 3 | `Those extra bytes` (19.22 → 29.62) | 10.4 s | Beat A, 19.22–23.9: a 10-cell byte grid with three dead cells (red dashed outline, X). The dead cells glitch-shake. `BYTES GO MISSING` pops @missing 22.72 and swaps to `MISSING BYTES: REBUILT` at "rebuilding" 21.56. Wait, 22.72 is after 21.56, so show `BYTES GO MISSING` from 19.22 (@Those extra bytes) and swap to `MISSING BYTES: REBUILT` at 21.56. At "recipe" (20.7) an amber recipe ring pulses out of an amber tray. At "rebuilding" (21.56) three amber repair chips arc from the tray into the three dead cells, staggered 0.4 s apart, each landing with a scale pop. Beat B, 23.94, "At the highest level": whip-through into the **hero** QR, 640 px, centred at y 740, with a gear logo. `LEVEL H` pops @H, 24.78. At 25.8, "scanner", the viewfinder locks on and a beam sweeps. **HERO from 26.62 "restore about 30%" to 29.62 (3.0 s):** about 30 % of the data/EC modules (6 blobs, red hatched) are punched out, never in the three finder squares, their separators, the timing lines, or the logo. Cyan outlines mark the finders. Amber parity arcs curve from the EC bytes into each gap. Repair-byte chips fly along the arcs and each flips its modules back to ink with a small shockwave. The cascade runs continuously across the 3.0 s. The QR drifts in a slow rotating glide (±2°, 1.0 → 1.06 scale), so nothing stands still for more than 0.3 s. `30% REBUILDABLE` pops @30% 27.52 and its counter ticks up. | glitch@Those extra bytes, punch@rebuilding, whip into hero @At the highest, glide + slow orbit through the hero, pull@30% | `BYTES GO MISSING` / `MISSING BYTES: REBUILT`; `LEVEL H` @H 24.78; `30% REBUILDABLE` @30% 27.52 | 2 |
| 4 | `So a logo` (29.62 → 41.08) | 11.5 s | Beat A, 29.62–33.4: QR (580 px, cy 650) with the logo growing from ~4 % to 12 %. Data modules ringing the logo flip amber and then repair themselves in a ripple, so the code moves the whole time. A green budget bar at the bottom shows `REPAIR BUDGET: 30%`. `PLANNED-FOR DAMAGE` pops @damage 31.52. Beat B, 35.4–38.2: at "15%" (35.90) the label `LOGO ≈ 15% OF AREA` pops and the bar counter ticks 0 → 15 %. A shockwave ring leaves the logo at "safe." (37.52). The camera glides across during the whole beat. Beat C, 38.32–41.08: the real torn-QR photo ProofCard (BOBMATH, CC0) zooms in on the missing chunk. A thin budget bar below it (y ≈ 1100) fills with a GLARE segment @Glare 38.32, then a SCRATCHES segment @scratches 39.18, both eating the **same 30 % bar**. `SAME 30% BUDGET` pops @same 40.04. | push@So a logo, glide@In real tests (continuous), pull@Glare | `PLANNED-FOR DAMAGE` / `LOGO ≈ 15% OF AREA`; `GLARE` @38.32, `SCRATCHES` @39.18, `SAME 30% BUDGET` @40.04 | 3 |
| 5 | `But cover` (41.08 → 48.08) | 7.0 s | The QR with the cyan-glow finders. At "three big corner" (42.58) a dark cover slides over the top-left finder and `CORNER SQUARE = FINDER` pops next to it @corner squares 42.58 (held until 43.7). At "over" (43.72) a hard shake: the Viewfinder flips red and a large `NO SCAN` solid red plate (≈ 600 × 120, ink text, 64 px) pops at the top of the stage and stays through 44.9. At "data." (45.10) `FINDER PATTERNS ≠ DATA` pops. From 45.1 to 48.08 the three finders glow and a lock-on reticle hops finder to finder (45.68, 46.14, 46.88), with a glide camera, so there is no still stretch. The QR is 560 px at cy 640, and the punch is s 1.1 / x 60 to keep ≥ 24 px of side margin. | push@three big corner, punch@it's over, pull@Those aren't data, glide@finds the code | `CORNER SQUARE = FINDER` @42.58; `NO SCAN` @it's over 43.72 (hud plate); `FINDER PATTERNS ≠ DATA` @data. 45.10 | 2 |
| 6 | `That's the mechanism` (48.08 → 49.42) | 1.3 s | Channel outro card with the gear stamp and sting. The only card, as in v6. | push | `THAT'S THE MECHANISM.` | 1 |
| 7 | `A QR code carries` (49.42 → loop) | ~4.5 s | QR (540) with the gear. At "carries" (50.54) 8 amber repair blocks fly in and dock around it in a settled ring. At "own" (50.98) the QR modules flip amber → ink as the blocks dock. `SPARE PARTS INCLUDED` pops @spare 51.32 as a scale-popped TagLabel. Everything is complete before `loop − 1.5 s`, where EpisodeShell freezes the stage. If that freeze point falls before 51.7, pull the docking earlier, but never pop the label earlier than 50.82. The shot ends in the loop whip into the hook. | pull@A QR code carries, then hold under the payoff freeze | `SPARE PARTS INCLUDED` @spare 51.32 | 1 |

**`shots.md` rows (the builder may edit this file and must keep every row true to the draw):**
- Row 1: `scale@This QR, push@Your camera, punch@anyway.`; text `THE CODE THAT REPAIRS ITSELF; LINK OPENS`.
- Row 2: add `DATA @data` and `= f(DATA) @data`, `REPAIR BYTES @adds extra bytes`, `REED-SOLOMON (1960) @Reed-Solomon`, `STILL PLAYING @scratched CDs`.
- Row 3: `hero@restore about 30%` (spoken "thirty percent", caption text `30%`; use the caption form so lint resolves it), `30% REBUILDABLE @30%`, `LEVEL H @H`.
- Row 4: add `GLARE @Glare`, `SCRATCHES @scratches`, `SAME 30% BUDGET @same`.
- Row 5: add `CORNER SQUARE = FINDER @corner squares`, `NO SCAN @over`, `FINDER PATTERNS ≠ DATA @data.`.
- Row 7: `SPARE PARTS INCLUDED @spare`.

## Key stills
Confirm these three before building the rest.

- **HOOK (frame 0).** The bright paper-white level-H QR fills the frame at a scale where the code width is about 1000 px, leaving a margin of at least 24 px per side. The amber gear logo spins in the centre. `THE CODE THAT REPAIRS ITSELF` sits as TitleHook at top 280, fully opaque. The stage is ≥ 12 % bright pixels. There is no card and no black frame. The chrome, captions and chapter deck sit in their usual bands.
- **MID (≈ 28.0 s, hero).** A 640 px QR is centred at about (540, 740) with its gear logo. About 30 % of the data modules are punched out as red-hatched blobs, and none touch the three cyan-outlined finder squares. Amber parity arcs curve from the EC bytes into the gaps. Several amber repair chips are mid-flight and some modules have already flipped back to ink with a small shockwave. `30% REBUILDABLE` is a Label near y 1080, clear of the right action rail. A scan beam crosses the code.
- **END (loop frame).** Identical to frame 0, via `LoopEnd`. The 8 docked amber blocks and `SPARE PARTS INCLUDED` are fully settled before the 1.5 s payoff freeze, then the whip hands over to the hook.

## Must fix
1. **Motion holds.** v6 had stills of 3.5 s at 30.6, 2.8 s at 45.1, 2.8 s at 24.8, 2.4 s at 5.5, 2.4 s at 35.9 and 2.3 s at 19.4. Fix:
   - 5.5: URL chars fly into byte chips.
   - 19.4: dead cells glitch and repair chips arc in.
   - 24.8: scanner sweep and `LEVEL H` pop, then the hero cascade.
   - 30.6: modules around the logo ripple and repair.
   - 35.9: 15 % counter tick, shockwave ring and camera glide.
   - 45.1: finder-hopping lock-on reticle and glide.
2. **Entrance snaps.** The snap at 43.8 s (tall element x 315–380), the badge snap at 43.4 s and the opacity-only fade at 15.1 s. All red-state changes and badges use `<Enter>` / `TagLabel` / `Badge` pops with scale anticipation. The `o` prop is scale, not opacity.
3. **Safe zone.** The label at x 892–936, y 950–994 (10.6–11.2 s) sat in the right action rail. The byte grid is narrowed to 6 × 100 px chips, x 130–830, so nothing is at x > 900, y > 900, even after a camera glide.
4. **Label persistence.** `THE CODE THAT REPAIRS ITSELF` stays through the full hook shot (binary switch at 5.1 s, no fade). `NO SCAN` is a large solid red plate with ink text, held ≥ 1.1 s.
5. **Label sync.** `DATA` and `= f(DATA)` pop at "data" (11.88) and `SPARE PARTS INCLUDED` at "spare" (51.32). Every label is timed to caption words (`at()`), never to round numbers.
6. **Sound-off clarity.** Add `GLARE` / `SCRATCHES` / `SAME 30% BUDGET` on one shared bar, and `CORNER SQUARE = FINDER`.
7. **Hero.** `hero@restore about 30%` is now the big centred, moving repair cascade (≥ 1.5 s, 3.0 s as drawn).
8. **Critic weaknesses.**
   - The damage mask never covers finders, separators or timing lines, and only data/EC modules are punched out.
   - Reconstruction is shown as chips flying into gaps along arcs, not a static grid.
   - Framing varies: hook zoom, wide byte grid, hero orbit, budget bar and photo, finder-hopping reticle. Never the same centred QR framing for long.
9. **Ghost text.** No `opacity` fades wrap text. Remove the opacity wrappers around the byte chips (`popOpacity` on a `<g>` holding a `Label`) and drive entrances with scale only. Hook title and CD card use binary switches or scale.
10. **Atomic text.** Only `Label` / `TagLabel` / `Badge` / `Pill` / `TitleHook`, no raw `<text>` / `<tspan>`. The type is mono hex in `Label` with `font={MONO}`.
11. **Side edges.** Hook frame-0 scale is reduced from 2.35× to about 2.0× (QR ≈ 1000 px), so the art is never cut by a side edge. The finder punch is capped (x 60) so the QR clears x > 900, y > 900.

## Gates
- **A1** Format: 1080×1920, 30 fps, H.264 + AAC 48 kHz, 35–55 s.
- **A2** Loudness: −15.5…−13 LUFS, true peak ≤ −1 dBTP.
- **A3 / A3b** SFX sit 10–16 dB under the voice, never closer than 8 dB, at 1.2–1.5 onsets/s.
- **A4** No stage hold over 2.0 s. The r9 target is a change every ≤ 1.75 s.
- **A5** Subject drawn at 0.3 s, visible change by 1.0 s.
- **A6** Exact loop: last → first frame step ≤ p95, PSNR ≥ 25 dB.
- **A7** `shots.md` lint: phrases resolve, no fades, ≤ 8 words, no three pushes in a row, beat every ≤ 3 s, first beat < 1 s.
- **A8** SFX onset density 1.2–1.5/s.
- **A9 / A9b** Label contrast ≥ 4.5:1 for held ≥ 0.6 s, including raw SVG `<text>` (which is banned here anyway).
- **A10** The end card lasts ≥ 1.0 s and the payoff is settled ≥ 1.5 s before the loop whip.
- **A11** Frame 0 and 0.3 s have ≥ 12 % bright stage pixels.
- **A12** All `Label` sizes ≥ 30 px.
- **A13** No label/pill occupancies closer than 36 px; no icon over a pill interior.
- **A14** Badge/pill entrances pop with anticipation/overshoot, never snap in.
- **A15** Text inside the Shorts safe zone and ≥ 24 px from the side edges (every hook frame in the first 2 s counts).
- **A16** No whole-stage card ≥ 55 % held ≥ 1.0 s, and boxed framing ≤ 50 % of runtime (the ProofCard window must stay short).
- **A17** ≤ 3 pill callouts at once, held ≥ 0.6 s.
- **A18** No decorative HUD or fake timecodes in source.
- **r9 additions:**
  - Static: raw `<text>` banned.
  - Ghost-text contrast gate.
  - Label sync (`label_sync.py`): OCR first-seen vs the aligned word, ±0.5 s.
  - Hero gate (`hero.py`): ≥ 35 % of stage, centred, moving, ≥ 1.5 s, no edge clip.
  - Art-edge gate: object fill running past a side edge ≥ 0.6 s fails.

## Do not
- Do not add slide-deck cards that enclose the stage. The ProofCard is brief, and the only whole-frame card is the outro.
- Do not use boxed panels for most of the video.
- Do not show more than 3 pills or callouts at once.
- Do not add decorative HUD, fake timecodes or `REC`-style text.
- Do not use raw SVG `<text>` or text under 4.5:1 contrast.
- Do not use cross-fades, or opacity fades on any group that contains text.
- Do not cover the three finders with the damage mask, or let the logo or anything else push art off a side edge.
- Do not add facts outside `facts.json` (30 % of codewords, ≈ 15 % of area, glare and scratches use the same budget, finders are not covered by error correction, Reed-Solomon 1960 and CDs).
- Do not change the narration, captions, audio or hooks.
- Do not repeat three pushes in a row, or hold the same centred QR framing for long stretches.
- Do not publish or upload. Human approval is required for the final cut.
