# VIDEO — Sky

**Goal.** The viewer has to understand that a sunset is the same scattering as the blue sky, seen from the other end of the beam. Air scatters blue about 4× more than red. At noon that scattered blue reaches you from every direction. At sunset the beam crosses dozens of times more air, so the blue is stripped out and the orange and red are left. The viewer should feel the click of "the blue they lost is the blue sky someone else is looking at." The video is one continuous sky world with no cards or panels. Frame 0 is the sun sitting on a bright horizon, already shedding blue sparks. The camera then moves through the air to a molecule, a blue-versus-red race, a noon dome, and an Earth cross-section. The hero moment is at "color someone else's afternoon": the stripped-out blue visibly streams around the planet and floods the far observer's sky. It ends with the beam landing bright orange in the sunset observer's eyes. Every beat shows its cause on screen, so a muted viewer gets the mechanism.

## Frozen script

> This is the sunset made of someone else's blue sky. Both are the same trick, seen from two places.
>
> Sunlight is every color mixed together. Air molecules are about a thousand times smaller than a light wave, and tiny things scatter short waves far more than long ones. Blue gets bounced around about four times more than red.
>
> At noon, you're seeing that scattered blue arriving from every direction. That's the sky.
>
> At sunset, the light reaching you crosses dozens of times more air. Along the way, the blue is scattered out of the beam, off to color someone else's afternoon. What survives to reach your eyes is orange and red.
>
> That's the mechanism. Your sunset is the leftovers of someone else's blue sky.

The narration is already voiced. Do not change, reorder or retime a word. Take every timing from `makeAt(words, fps)` on `03-sky.captions.json`. The durations below are estimates only.

## Shots

**World rules for the table**
- One full-bleed sky gradient fills the whole 1080×1920 frame in every shot. It runs from deep blue at the top to orange at the horizon, and it re-tints per beat.
- No `backdrop="library/sky_sunset.jpg"`, no city skyline, no giant gears. Pass no backdrop, or a pure gradient sky layer.
- The **Sun** is the persistent subject. It is the same disc and the same gradient in every shot, and its x is always ≤ 880.
- The **blue/orange light streams** are the second persistent subject. They are the same particle system carried from shot to shot.
- Camera moves are world moves only. Most transitions are a push-through into the next part of the same sky, with a whip or whipUp where the table says so.
- No `<ProofCard>` panel. The ISS photo is a full-bleed window layer (shot 9).

| # | Caption anchor | Dur (est.) | ONE continuous-world visual idea | Camera | On-screen text (≤2 levels, ≤6 words each) | Max callouts |
|---|---|---|---|---|---|---|
| 1 | "This is the sunset made of someone else's blue sky" | 0.0–4.2 s | **Frame 0 is the subject.** A full-bleed bright dusk sky with a large sun half-set on the horizon, fully inside the frame (sun disc x 200–880, nothing clipped). An orange beam leaves the sun, and bright blue sparks peel off it sideways and rise into the upper sky. This is the whole thesis in one image. There is no title box and no split panels. | Slow glide-up, scale 1.0→1.06, no zoom-in start. Frame 0 is at rest scale. | L1: "SOMEONE ELSE'S BLUE SKY" (on the sky over a soft gradient scrim, not a box). L2: "SUNSET" (≥30 px, x ≥ 90). | 1 |
| 2 | "Both are the same trick, seen from two places" | 4.2–7.0 s | The sky above the horizon *turns noon-blue* by wiping up from the horizon. Blue sparks stream up into it, so one sky holds both times of day. A small amber pill pops in with overshoot (anticipation then overshoot). | cut+punch on "same trick", scale 1.05, centred on the sun | L1: "SAME TRICK" | 1 |
| 3 | "Sunlight is every color mixed together" | 7.0–10.0 s | The sun's beam, still in the sky, enters a glass prism drawn in the air. Seven spectrum rays fan out and keep travelling across the sky toward the next beat. | push-through along the beam | L1: "SUNLIGHT" → "EVERY COLOR" | 1 |
| 4 | "Air molecules are about a thousand times smaller than a light wave" | 10.0–14.5 s | Push into the air until one N₂/O₂ molecule fills the middle. A **large** blue wave and a **long** red wave arrive from the left on the same axis. The molecule is drawn tiny next to the wavelength, with a bracket "~1000× smaller". The label sits above the molecule, in clear space. Nothing else is drawn here, so no ray or badge can cross it. | push (1.0→1.15), then glide | L1: "N₂ / O₂ MOLECULE". L2: "~1000× SMALLER" (≥36 px gap from every other element) | 2 |
| 5 | "and tiny things scatter short waves far more than long ones" | 14.5–18.0 s | **The wave visibly strikes the particle.** The blue sine wave's front reaches the molecule, which flashes and kicks (squash/overshoot). Blue scatter rays then burst outward from the point of impact, starting at the molecule edge and away from all labels. The label has already faded to a corner tag at the top. The long red wave passes through the molecule's position with only a faint wobble. | punch on the impact (1.08), then pull | L1: "SHORT WAVES SCATTER" | 1 |
| 6 | "Blue gets bounced around about four times more than red" | 18.0–22.0 s | The sky world holds. Two parallel light beams of equal length run through a band of air molecules (small dots hanging in the sky, no card). The **blue beam sprays 4 spark bursts, the red beam sprays 1**, as live counts. Each burst lands with a thud and the tally ticks. No formula and no 450/650 nm text; "4×" and "1×" are the numbers. | push, then punch on "four times" (≤1.08, all text x ≤ 900) | L1: "BLUE 4×". L2: "RED 1×" | 2 |
| 7 | "At noon, you're seeing that scattered blue arriving from every direction" | 22.0–27.0 s | whipUp into a **noon dome**: a tiny observer on a dark ground strip at the bottom, the sun high at upper right and a short white beam. Blue scatter arrows fill the *whole dome above the observer* and curve in toward the eyes from every side, so the blue fan goes up and inward, never out to space. The pill "YOU, AT NOON" sits on the dark ground strip, not over art. | glide, then push on "scattered blue" | L1: "YOU, AT NOON". L2 on "That's the sky": "THAT'S THE SKY" | 2 |
| 8 | "At sunset, the light reaching you crosses dozens of times more air" | 27.0–32.0 s | pull out to a full Earth cross-section, drawn as one continuous diagram on the sky. It has a thin atmosphere shell, the sun far right and a sunset observer on the left limb. The beam is a long bright strip grazing the *whole* shell, with a brace beside the noon path (tiny) and this path (long). | pull (the noon dome becomes the planet's top) | L1: "DOZENS × MORE AIR" | 1 |
| 9 | "Along the way, the blue is scattered out of the beam," | 32.0–34.2 s | **The ISS photo is a full-bleed window, not a card.** The real NASA photo fills the stage edge to edge, with no diagram behind it and no sun peeking out. A slow push (1.04→1.12) runs while a thin blue→red gradient sweep runs along the limb. The credit is ≥30 px, in two lines, inside y 290–1190 and x 24–900. It is on screen ≤2.4 s. | glide + push, no punch | L1: "SEEN FROM THE ISS". L2 (credit): "NASA ISS028-E-007274 · PUBLIC DOMAIN" | 2 |
| 10 | "off to color someone else's afternoon." (**hero**) | 34.2–38.0 s | Cut+punch back to the Earth diagram. The blue sparks peel off the sunset beam and **fly around the planet limb in a sweeping arc**, a time-lapse flow that leaves a glowing trail. They land on a second observer on the far side, whose sky dome floods from dark to bright blue in a ripple as the sparks arrive. The ground foley is a rising shimmer. A pill appears only once the ripple has landed. | glide following the stream (1.0→1.1), then pull to show both observers | L1: "SOMEONE ELSE'S AFTERNOON" | 2 (this pill plus the sunset-observer tag; no others) |
| 11 | "What survives to reach your eyes is orange and red." | 38.0–41.0 s | The beam exits the thick air **bright orange to red** and lands on the sunset observer's eyes, with a big warm bloom. The whole frame stays **bright**. No dimming layer sits under captions or pills. The Sun stays fully in frame at x ≤ 880 throughout. | slow push centred on the observer only, max scale 1.06, **no punch that moves the Sun** | L1: "ORANGE + RED SURVIVE" (amber on ink pill, ≥7:1) | 2 (pill plus observer tag) |
| 12 | "That's the mechanism." | 41.0–43.2 s | The sky turns to the end-card world: a "THAT'S THE MECHANISM." lockup stamped on the sunset sky with the gear, signature sting. The card holds until the word "mechanism" ends in the captions plus ≥0.5 s, and never less than 1.5 s. The next shot's first caption word must not appear before the card ends. | riser into the card, then push | L1: "THAT'S THE MECHANISM." | 1 |
| 13 | "Your sunset is the leftovers of someone else's blue sky." | 43.2–46.2 s | One continuous sky: noon-blue above, the sunset horizon below, the same sun. Blue sparks drift up out of the sunset into the blue sky. There are **no split panels**, just the frame-0 world, settling into the hook so the loop seam is invisible. The final frame is the frame-0 composition at rest. | slow pull (1.06→1.0), a small whip on the last 6 frames **that lands exactly on frame 0** | L1: "SAME LIGHT, LATER" (≤1.5 s, then clear before the loop) | 1 |

## Key stills

**HOOK (frame 0).** The full 1080×1920 frame is a bright dusk sky, deep blue at the top running to orange at the horizon. The horizon sits at about y 880. A large sun, about 340 px wide, is half-set on the horizon at x≈540. All of the disc is inside x 200–880 and nothing touches the frame edge. A glowing orange beam leaves the sun to the left. Six to eight bright blue sparks have already peeled off it and drift up into the sky. L1 is "SOMEONE ELSE'S BLUE SKY" in paper white on a soft gradient scrim, at y≈330. L2 is "SUNSET" at 36 px over the dusk glow, x≥90, never clipped. There is no title box and no card. Over 12 % of stage pixels are brighter than 90/255. It has motion from 0.3 s: the sun sinks, the sparks rise and the beam shimmers.

**MID (core mechanism, shot 10, ~36 s).** The Earth cross-section sits on the continuous sky with the atmosphere shell glowing. The sunset observer is at the left limb. A long orange beam grazes the shell and a stream of ~20 bright blue sparks has peeled off it. It sweeps along the limb in a glowing arc to the second observer on the far side. That observer's dome is half-flooded with blue, with the ripple front visible. The sun is fully in frame at x≈800. Only the pill "SOMEONE ELSE'S AFTERNOON" and one observer tag are on screen. Captions are full-opacity, amber on the active word.

**END (loop frame).** Identical to HOOK: the same horizon, sun position, sparks and sky gradient, and the same text state as frame 0. `LoopEnd` locks it. The whip into frame 0 uses a sharp, not blurred, landing, so the seam PSNR is ≥ 25 dB.

## Must fix

| Problem (previous version) | Fix |
|---|---|
| **[blocker] 00:38–00:40: captions and the "ORANGE + RED SURVIVE" pill dim to 25–35 % on dark ground, and the camera zoom slices the Sun off the right edge.** | The caption layer is outside the camera and outside any dim or fade tied to shots, and sits at opacity 1.0 for every word. Shot 11 keeps the stage bright and has no dim or vignette layer under the captions. The pill is amber on ink at ≥7:1 and stays up for the whole of "orange and red". The Sun is pinned inside x ≤ 880. Shot 11's camera is a push with scale ≤1.06 centred on the observer and no punch. The builder must find what dims the captions and pill at that moment (probably a card/`cardAt` fade or the `hud` opacity) and remove it. Check the frames at 38.0, 38.5, 39.0, 39.5 and 40.0 s. |
| **[blocker] 00:00 / 00:46: opens mid-zoom, "SUNSET" clipped to "UNSET", blurred whip into a broken frame, bulky title box.** | Frame 0 is a rest frame. The old zoom 2.25→1.0 is deleted, along with `TitleHook` backing boxes and the split-panel Split component. Every hook label sits at x ≥ 90 and inside the frame, and the loop whip lands sharp on the identical frame-0 composition (`LoopEnd`). Whip blur is symmetric and stops ≥4 frames before the last frame. Check frames 0 and D-1 in `transitions_it*.png`. |
| **[major] 00:15–00:17: scatter lines cross "N₂ / O₂ MOLECULE" and the wave floats far from the molecule.** | Shots 4–5 are redrawn. The wave front travels on the molecule's own axis and strikes it, then the scatter rays start at the molecule's edge. The label sits above, in a reserved clear zone, and goes to a corner tag at impact. Use `Lane` / `LabeledBox` for clearance, and keep every ray ≥36 px from any label (A13). |
| **[major] 00:35–00:40: the hero payoff is static sticks and a thin line.** | Shot 10 is the hero. Blue sparks stream around the planet limb with a trail and flood the far observer's sky with a ripple. Shot 11 lands a bright orange beam with a bloom. Foley: rising shimmer on the stream, a soft warm "arrive" thud on the beam landing. |
| **[major] Static holds 2.2–3.0 s (00:01–03, 08–09, 15–17, 19–21, 24–26, 32–34, 43–45); badges fade linearly; the Rayleigh bar chart reads like a slide.** | Each shot has a persistent moving element: drifting sparks, a pulsing sun, shimmer on the beams and slow-moving air dots. Every badge uses `Pill`/`TagLabel` pop (anticipation then overshoot), never a linear fade. The bar chart is gone, replaced by live spark counts in the sky (shot 6). The 1/λ⁴ formula is removed. |
| **[major] 00:07–00:40: the persistent city skyline and giant gears behind everything.** | No `sky_sunset.jpg` backdrop, no skyline, no big gears. Backgrounds are a per-beat sky gradient (prism sky, deep-blue molecule zoom, noon dome, space-dark shell for the Earth) with the sun and sparks as continuity. Only the small brand-chip gear stays. |
| **[major] 00:32–00:34: the ISS card leaves the Sun poking out, the credit is ~20 px, and the photo holds still ~2.5 s.** | The photo is a full-bleed window with no diagram or sun behind it. The credit is ≥30 px on two lines, inside the safe zone. The photo holds ≤2.4 s with a slow push and a limb sweep, so A4 passes. |
| **[major] 00:00–00:46: the same air-whoosh on every cut, glassy UI pings, 1 s dead silence at 00:45.** | Build a bespoke foley map, with ≥6 distinct sources, using only SFX already licensed in `sfx/CREDITS.csv`. It has a soft air-sweep for push-throughs and a short low "whip" for whips. There is a glass-ting for the prism, a tick-and-flick on the molecule hit and a bright "spark" tick per scatter burst. It has a rising shimmer for the hero stream and a warm swell for the beam landing, plus the riser into the card and the sting on the catchphrase. A quiet ambient bed fills 43–46 s. Keep SFX at 1.2–1.5 onsets/s, 10–16 dB under the voice. |
| **[major] 00:41–00:42: the end card holds ~1 s and cuts before the catchphrase finishes, stranding "the mechanism. Your".** | The card holds until "mechanism" ends in the captions plus ≥0.5 s, and ≥1.5 s overall. `cardUntil` is derived from the caption word timings, never hard-coded. The first word of the final shot ("Your") must start after the card clears (A10). |
| **[minor] 00:22–00:26: "YOU, AT NOON" over the coastline, and the blue fan points to space.** | The noon dome has a dark ground strip with the label on it, and the blue fan fills the dome above the observer and bends inward. |
| **[pairwise] Pill clustering around Earth at 0:35 (4 pills) and the 0:34–0:38 callout pile-up.** | Max 3 callouts at once (A17), and the table never exceeds 2 in the Earth shots. Observer tags and the "DOZENS × MORE AIR" brace are shown one at a time. |
| **[pairwise] Rays touch "~1000× SMALLER" at 0:12; the scale badge is sandwiched between two wave paths at 0:11.** | The scale badge sits in its own clear band, and waves are drawn after the badge fades. ≥36 px clearance (A13). |
| **[pairwise] Rayleigh equation density at 0:18; the skyline behind abstract shots 0:08–0:19.** | Drop the equation, and no skyline behind abstract shots. |
| **[pairwise] The ISS card at 0:31 hides the Earth ray diagram; the final punch-in at 0:45 is too rapid.** | The photo is a deliberate "window cut" into a bounded beat. Shot 13 settles with a slow pull, ≥1.5 s of settled hold, and the whip only in the last 6 frames. |
| **[r7 gate, framing.py] whole-stage card held 18.4–20.2 s (the ratio beat) and 42.4–46.2 s (callback split panels).** | No whole-stage rect/card in any shot. The ratio beat and the callback are open sky with no containing panel (A16, boxed framing ≤50 % of runtime and no whole-stage card ≥1 s). |

## Gates

The build must pass all of these. Run `scripts/iterate.sh <N> Sky` and read `qa/Sky/report_it<N>.json`, `grid_it<N>.png` and `transitions_it<N>.png`.

- **A1:** 1080×1920, 30 fps, H.264 + AAC 48 kHz, 35–55 s.
- **A2:** integrated loudness −15.5…−13 LUFS, true peak ≤ −1 dBTP.
- **A3:** median SFX peak 10–16 dB under the voice, none closer than 8 dB.
- **A3b / A8:** 1.2–1.5 SFX onsets per second.
- **A4:** no stage hold > 2.0 s.
- **A5:** the hook subject is drawn at 0.3 s and there is a visible change by 1.0 s.
- **A6:** exact loop, seam jump ≤ p95 of normal steps, PSNR ≥ 25 dB.
- **A7:** storyboard lint (phrases resolve, no fades, ≤8 words per text, no 3 pushes in a row, a beat every ≤3 s, first beat < 1 s). `shots.md` must be regenerated to match this table.
- **A9:** label and pill WCAG contrast ≥ 4.5:1 (held ≥ 0.6 s). This includes captions at 38–40 s and any raw SVG text.
- **A10:** the end card holds ≥ 1.0 s (plan: ≥ 1.5 s), and the payoff settles ≥ 1.5 s before the loop whip.
- **A11:** frame 0 and 0.3 s have ≥ 12 % bright stage pixels (> 90/255).
- **A12:** every `<Label size>` is ≥ 30 px.
- **A13:** no two labels or pills closer than 36 px and no icon covering a pill, held ≥ 0.6 s.
- **A14:** badge and pill pops have anticipation/overshoot. Use the primitives (`TagLabel`, `Pill`).
- **A15:** text inside the safe zones and ≥ 24 px from the left/right edge, held ≥ 0.6 s. Re-check after every camera move.
- **A16 (`scripts/framing.py`):** no whole-stage card ≥ 1 s, and boxed framing ≤ 50 % of runtime.
- **A17 (`scripts/contrast.py`):** ≤ 3 pills or badges on screen at once.
- **A18 (`scripts/static_gates.py`):** no decorative HUD or fake timecode strings.
- **Photos:** the NASA ISS photo has a `CREDITS.csv` row and a PD licence (`photo_credits.md`). Run `scripts/facts.py check 03-sky` before any voicing change (there should be none).
- **Visual review:** the V1–V5 sheets show no clipped labels, no sun cut off, no empty half and no triple push.
- **Independent pairwise critic:** it must prefer Sky_v7 over Sky_v5 in **both** orders. The builder does not grade itself.

## Do not

- Do not enclose the stage in slide-deck cards, title boxes or dark panels, and do not use boxed panels for most of the video (no whole-stage card ≥ 1 s).
- Do not show more than 3 pills or callouts at once. The plan targets ≤2.
- Do not add decorative HUD, fake timecodes or counters that carry no information.
- Do not use raw SVG `<text>` under 4.5:1 contrast. Use `Label`, `Pill` and `TagLabel`.
- Do not use cross-fades between sections. Use push-through, whip, whipUp or cut+punch.
- Do not add facts beyond `facts.json`. That means the ~1000× smaller, the ~4× blue vs red, "dozens × more air" and the "same scattering seen from another angle" framing. Do not show "30×". Do not show Rayleigh or the 1/λ⁴ formula, which are cut for density.
- Do not open on a zoomed, cropped or blurred frame, a title card or a split panel.
- Do not reuse the city skyline or giant faint gears behind any shot.
- Do not let a camera punch push the Sun, a label or a pill past x 900 or off the frame.
- Do not change the voiced script, publish, schedule or upload anything. The angle, script and final cut need human approval.
