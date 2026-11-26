# VIDEO — Elevator

**Goal.** The viewer should leave knowing that an elevator is a balance, not a hoist. The counterweight is built to match the empty car plus about 40–50 % of the rated load. The motor therefore only fights the *difference* between the two sides. The viewer should feel the small surprise of the special moment: release the brake on an empty car and it rises, because the counterweight is the heavier side. That moment is the empty car rising with amber floor-speed streaks and a chevron arrow while "EMPTY CAR RISES" lands. The payoff is "A SCALE, not a crane", which ends on a settled balance and loops back to the bright car at frame 0.

This is a revision pass. The look, timing, shot order and narration of `remotion/src/episodes/Elevator.tsx` are kept. Only these changes are applied:
- floor-marker contrast
- hook-title clearance and edge margin
- spring/overshoot entrances (MOTOR badge and all new elements)
- a DIFFERENCE keyword at "It only fights the difference."
- real motion beats so nothing on the stage holds longer than 1.75 s

## Frozen script

Already voiced. The builder must not change a word.

```
This is the elevator that barely lifts you. It almost balances you.

On the other side of the cable hangs a counterweight. It's built to match the empty car, plus about forty to fifty percent of the rated load.

So the motor never hauls the full weight. It only fights the difference. When the car is full, the motor helps it up. When the car is nearly empty, the counterweight is the heavier side, and the motor holds it back.

Here's the strange part. Release the brake on an empty car, and it wouldn't fall. It would rise.

That's why a modest motor can move a full office of people, all day long.

That's the mechanism. An elevator is a scale, not a crane.
```

## Shots

One persistent rig (car, shaft, counterweight, main + deflector sheaves, motor, brake) is shared by shots 1–5. The camera moves around that world. Times are approximate and come from `captions.json`. The builder must keep using `at("<phrase>")` anchors, not hard-coded frames.

| # | Caption anchor | Duration (est.) | Continuous-world visual idea | Camera | On-screen text (≤2 levels) | Max callouts |
|---|---|---|---|---|---|---|
| 1 | "This is the elevator" (0 s) → "almost balances" | 0–4.6 s (4.6) | Frame 0 is already the bright cutaway hoistway, tight on the lit car with 2 riders. The scale reveal pulls out over about 1.2 s to the full shaft, counterweight and sheaves. The car rises with a gentle bob. A spring-pop "≈ BALANCED" tag lands at "almost balances", and the counterweight lights teal. | Scale-reveal pull-out from 1.95× to 1.0×, then glide | L1 title "THE ELEVATOR THAT / BARELY LIFTS / YOU". L2 "≈ BALANCED". | 2 |
| 2 | "On the other side" | 4.6–13.7 s (9.1) | The camera travels along the cable to the counterweight and deflector sheave. The counterweight's lower 38 % fills amber, which is the "empty car + 40–50 % load" split, with a plate-stack fill. | glide → push ("It's built") → glide ("plus about") → pull ("rated load") | L1 "COUNTERWEIGHT". L2 "= EMPTY CAR", "+ 40–50% LOAD". | 3 |
| 3 | "So the motor" → "fights the difference" → "car is full" → "nearly empty" → "holds it back" | 13.7–26.9 s (13.2) | Live weight bars (car vs counterweight) with opposing force arrows. The MOTOR badge on the machine pops at "motor". The amber DIFFERENCE keyword pops at "difference" next to the amber gap segment. The car fills with riders and the motor helps it up. The riders then leave and the car is driven down against the heavier counterweight as the torque arrow flips to "holds it back". | pull → punch ("fights the difference") → push ("car is full") → punch ("nearly empty") → glide ("heavier side") | L1 "MOTOR", "DIFFERENCE", "MOTOR HELPS IT UP", "MOTOR HOLDS IT BACK". L2 bar legend "CAR", "CW". | 3 |
| 4 | "Here's the strange" | 26.9–33.1 s (6.1) | Caliper brake shoes close on the main sheave (red "BRAKE ON"). They then spring open (amber "BRAKE OFF"). The empty car creeps, then shoots up. The counterweight drops and amber floor-speed streaks and chevrons trail the car. | push → punch ("It would rise") | L1 "BRAKE ON/OFF". L2 "IT WOULDN'T FALL" → "EMPTY CAR RISES". | 2 |
| 5 | "That's why a" | 33.1–37.9 s (4.8) | The motor lights amber and the car carries riders up and down. At "full office" the real HABS/LoC public-domain photo proof card (the traction machine) opens, with its focus ring on motor + drive sheave. | glide → pull ("full office") | L1 "SMALL MOTOR · FULL OFFICE". L2 "TRACTION MACHINE" (inside the ProofCard). | 2 |
| 6 | "That's the mechanism" | 37.9–39.2 s (1.3) | The channel outro card. The gear stamps and the sting lands. | push in, push out | "THAT'S THE MECHANISM." | 1 |
| 7 | "An elevator is a" | 39.2 s → loop (≈4.5) | Two stage panels. On the left, a scale beam tips, rebounds and locks level with CAR and CW blocks dropping on, and a green check pops. On the right, the crane is struck through in red. A shockwave ring and squash follow the lock. Micro-motion keeps it alive until the whip back to frame 0. | push in, whip out to loop | L1 "A SCALE", "A CRANE". | 2 |

### Beat schedule for the shot 3 and 4 rewrite

Shot 1 and the rest of the rig keep their existing keyframes.

- **Shot 3, "motor" (14.1 s):** the MOTOR badge spring-pops. It anticipates to 0.85, overshoots to 1.12, then settles to 1.0.
- **Shot 3, "difference" (17.5 s):** the DIFFERENCE keyword spring-pops in amber and replaces the old "MOTOR = DIFFERENCE" tag. The CAR/CW legend collapses out (shrink-pop out) at that beat so at most MOTOR, DIFFERENCE and one other callout are up.
  - It holds until "helps" (20.0 s), then "MOTOR HELPS IT UP" takes over.
  - From "nearly" (22.0 s) the fallback text is "DIFFERENCE". "MOTOR HOLDS IT BACK" pops at "holds" (25.7 s).
- **Shot 3, "full" (19.2 s):** the car loads riders, one pop about every 4 frames. It rises 720 → 675 with eased overshoot.
- **Shot 3, "nearly empty" → "holds it back" (22.0–27.7 s):** this replaces the old static 6 s hold. The riders shrink out one at a time about every 0.4 s. The car then travels continuously from y 675 to 845 (about 34 px/s), eased and driven by the motor against the heavier counterweight.
  - At "heavier side" (24.2 s) the torque arrow flips with a spring pop.
  - At "holds" (25.7 s) the sheave gets a small squash-and-stretch strain pulse.
  - Keep the strain jitter as secondary motion only.
- **Shot 4, "Release" (28.8 s):** the brake shoes close, then open (about 0.4 s apart). The shudder stays.
- **Shot 4, "brake" → "wouldn't fall" (29.2–31.5 s):** replaces the old 3 s freeze at y 845. The sheave starts turning slowly and the counterweight begins to sink. The car creeps up about 25 px with eased motion. At "wouldn't fall" the car gives a small sag-and-recover (±8 px).
- **Shot 4, "rise" (32.2 s):** the car rises fast to y 625 with the amber streaks. A shockwave ring expands off the car at the start of the rise (continuous burst, not a static star).
- **Shot 5, "full office" → "people" → "all day long" (35.5–37.9 s):** the ProofCard's inner pan/focus keeps moving. The focus ring pulses at "people" (36.0 s) and again at "all day" (36.6 s) so the 2.4 s card never sits still.
- **Shot 7, after "not a crane" (41.5 s → loop):** the beam keeps its ±0.7° float. The crane hook swings. A soft expanding ring pulses off the green check, and an amber sheen sweeps the beam about every 1.2 s. The state stays settled while the stage keeps moving.

## Key stills

- **HOOK (frame 0).**
  - The subject is already on screen and bright: a tight 1.95× view of the cream-coloured cutaway hoistway with the lit elevator car, its amber outline, two riders and the "CAR" tag. The nearby shaft rails and guide shoes are visible.
  - The three-line title "THE ELEVATOR THAT / BARELY LIFTS / YOU" sits in the stage band, starting at y ≥ 300 and clear of the brand chip (y < 290).
  - Every title edge is ≥ 24 px from the left and right frame edges. Its bottom sits ≥ 36 px above the top of the car art and the "CAR" tag, by adjusting zoom focus or title size, not by removing the car from view.
  - It is not a title card: the car is already moving (bob) and the hoistway is lit. At least 12 % of stage pixels are bright (>90/255).
  - The floor markers L08…L01 on the left shaft margin are legible on every sampled frame at this zoom.
- **MID (core mechanism, about 17.8–18.5 s, "It only fights the difference").**
  - The full shaft is visible, with the car at left and the teal counterweight at right. The cables run over the main sheave, which has an amber dashed torque arc, and over the deflector sheave.
  - Gravity arrows hang below both bodies, with lengths showing weight.
  - The weight-bar panel at left (x ≥ 64) shows the white CAR bar and teal CW bar, with the amber segment marking the gap. The legend pills are already collapsing out as DIFFERENCE arrives.
  - The amber **DIFFERENCE** keyword has just spring-popped (scale ~1.1) and is centred at y ≈ 1150, with MOTOR already shown on the machine.
  - The pills in this frame number at most 3.
- **END (loop frame).** The last frame is identical to frame 0: the same 1.95× bright car, rider and title (`LoopEnd`/`LoopBack`). The scale/crane payoff has settled for ≥ 1.5 s, then whips back into the hook. Seam PSNR ≥ 25 dB.

## Must fix

These come from the revision brief and from what the current code shows. Only the brief's own items are attributed to the brief. I did not read any critic or QA report files, so nothing here is quoted from them.

1. **Floor-marker contrast.** The raw SVG `<text>` markers `L01–L08` use `#9BA3B0` at 0.8 opacity. Under the 1.95× opening zoom and the glides they can sit over the bright cream hoistway, where contrast is below 4.5:1.
   - Fix: draw each marker as paper `#F3EFE6` text, full opacity, on a small ink backing chip (≥ 7:1).
   - Fix: keep the markers ≥ 24 px from the left edge at every camera state.
2. **Hook-title clearance and edge margin.** `TitleHook` is at `top={278}`, which is inside the brand-chip zone (< 290). It is tight against the car art at frame 0.
   - Fix: move the title to y ≥ 300.
   - Fix: keep it ≥ 24 px from both side edges for every sampled frame in the first 2 s (A15, every frame counts there).
   - Fix: keep ≥ 36 px between the title and the car/CAR tag.
3. **Snap-in entrances.** The ≈ BALANCED, COUNTERWEIGHT, "= EMPTY CAR", "+ 40–50% LOAD", BRAKE ON/OFF and force-arrow elements ease opacity only. The MOTOR badge has no entrance at all.
   - Fix: every new or reworked element enters with anticipation, overshoot and settle (the brand `Enter` component if present, otherwise `pop()` / `popScale()` / `popOpacity()`).
   - Fix: the MOTOR badge pops at "motor" and re-pops when it turns amber at "modest motor".
4. **Missing DIFFERENCE keyword.** Add the one-word amber "DIFFERENCE" keyword at "It only fights the difference." The old "MOTOR = DIFFERENCE" tag is removed. The other text in that window follows the beat schedule above.
5. **Hold at "nearly empty".** The car is parked at y 675 from about 21 s to 27 s, with only a 2.4 px jitter. That is a hold well over 1.75 s.
   - Fix: replace the hold with the rider exits, continuous descent and torque-arrow flip described in the beat schedule.
6. **Hold after the brake opens.** The car sits at y 845 from about 29 s to 31.5 s with only a 0.5 s shudder.
   - Fix: the slow creep and sheave/counterweight start described above, plus the "wouldn't fall" sag-and-recover.
7. **Holds in the proof card and the end.** The ProofCard and the final settled scale could sit static for over 1.75 s.
   - Fix: add the focus-ring pulses, hook swing, ring pulses and sheen sweep described above. Nothing on the stage may sit still for more than 1.75 s (preview approximates this, `qa.py` measures it on the render).
8. **Pill count in shot 1.** "≈ BALANCED" and the title overlap for about 0.7 s.
   - Fix: run `scripts/preview.py` and confirm the pill-shaped callouts, including title backings, never exceed 3 for ≥ 0.6 s. If they do, delay "≈ BALANCED" until the title has faded.

## Gates

- **A1 Format:** 1080×1920, 30 fps, H.264 + AAC 48 kHz, 35–55 s.
- **A2 Loudness:** integrated −15.5…−13 LUFS, true peak ≤ −1 dBTP.
- **A3 SFX under voice:** median SFX peak 10–16 dB under the voice, none closer than 8 dB.
- **A3b/A8 SFX density:** 1.2–1.5 onsets/s. New pops must be paired with a cue (existing `cue()` list), not left silent.
- **A4 Motion:** no stage hold > 2.0 s (the target for this revision is ≤ 1.75 s).
- **A5 Hook visual:** subject drawn at 0.3 s and a visible change by 1.0 s.
- **A6 Exact loop:** last→first seam ≤ p95 of normal steps, PSNR ≥ 25 dB.
- **A7 Storyboard lint:** phrases resolve, no fades, ≤ 8 words per text, no three pushes in a row, a beat every ≤ 3 s.
- **A9 Label contrast:** Label and Pill text ≥ 4.5:1 WCAG, failing if held ≥ 0.6 s.
- **A9b Raw SVG `<text>`:** same contrast, safe-zone, clearance and clutter checks as A9. This covers the floor markers.
- **A10 End card:** "That's the mechanism" card ≥ 1.0 s, payoff settled ≥ 1.5 s before the loop whip.
- **A11 Hook brightness:** frame 0 and 0.3 s have ≥ 12 % bright stage pixels.
- **A12 Label size:** every `<Label size>` ≥ 30 px.
- **A13 Label spacing:** no two labels/pills within 36 px, no icon over a pill, held ≥ 0.6 s.
- **A14 Badge motion:** badges and pills pop with anticipation/overshoot, never snap in at full size. This covers the MOTOR badge and the DIFFERENCE keyword.
- **A15 Safe zones:** text inside the Shorts UI zones and ≥ 24 px from the side edges. In the first 2.0 s every frame counts, so the hook title is covered.
- **A16 Framing:** no whole-stage card held ≥ 1.0 s, and boxed framing ≤ 50 % of the runtime.
- **A17 Callout clutter:** ≤ 3 pill-shaped callouts at once, held ≥ 0.6 s.
- **A18 No decorative HUD:** no `00:12`, `REC`, `T+3`, `60 FPS`, `ISO 100`, `HUD` strings.
- **r8 gates, same run:**
  - caption ghost frames
  - meaningful-motion hold
  - entrance easing
  - frame-1 hook
  - first on-screen line
  - sound-off clarity
  - floating-callout clutter

## Do not

- Do not add slide-deck cards that enclose the stage.
- Do not use boxed panels for most of the video. The bar panel and the shot 7 boxes are the only framed areas.
- Do not show more than 3 pills at once.
- Do not add decorative HUD elements or fake timecodes.
- Do not use raw SVG text below 4.5:1 contrast.
- Do not use cross-fades between sections. Transitions are push, whip, whipUp or cut+punch.
- Do not add new facts that are not in `facts.json`.
- Do not change a word of the narration or the caption timing.
- Do not drop the real HABS/LoC photo proof card or its credit line.
- Do not publish, upload or schedule anything.
