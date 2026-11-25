# Round 2 — render → review → fix log

Each iteration = `scripts/iterate.sh <N> QR Elevator Sky` (shot lint → render → scripts/qa.py), then a visual review of
qa/<Id>/transitions_it<N>.png (8 frames in 0.8 s around every shot boundary + the loop seam) and grid_it<N>.png.
Reports: qa/<Id>/report_it<N>.json. Timings: metrics/runs.jsonl.

## Iteration 0 — stills (before the first full render)
- New brand kit + 3 episodes ported; first stills of QR.
- Found: Finders punch (1.32×) pushed the QR off-frame and the "NO SCAN" pill into the deck. → punch 1.2×, pill moved.

## Iteration 1 — first full v2 renders (render not yet instrumented, ~1 min each)
Automated: QR hold 5.2 s (Repair after the bars); Elevator hold 8.4 s + hook too dark for the detector; Sky hold 3.4 s, hook change 0.79 (<1).
Storyboard lint (new): 9 failures — gaps of 3.2–7.6 s without a beat, a hook with no beat in the first second, three pushes in a row (Sky).
Visual: QR byte grid off-centre / half-empty stage, Repair boxes pushed under the brand tag by a punch; Elevator count bars in the
right-hand platform column (x>900); Sky hook panel pushed under the brand chip, Earth+labels pushed into the captions, labels clipped at the left edge.
Fixes:
- Kit: new `hud` layer on `<Shot>` — verdict pills are screen-space, so camera punches can never push them into captions (all 3 episodes).
- Beats added to fill every >3 s gap (QR: "= f(DATA)", "30%" glide, "= PLANNED-FOR DAMAGE", 15 % marker, restore pulse; Elevator: counterweight tick, "full weight" glide, "helps it up", "heavier side" glide, "all day long" push; Sky: light-wave tick, short-waves pull, "four times" punch, "Along the way" glide, afternoon pop).
- Camera: Sky noon push→glide (no triple push), all Earth offsets reduced, Earth moved up/smaller (EY 840→740, R 250→210); QR bytes grid centred (+67 px).
- Elevator bars moved to the left (x 60/140); Sky hook sun drop in the first second.
- QA: motion detector switched to a 0.2 s window (catches eases/fades), hook brightness threshold for dark palettes.

## Iteration 2
Automated: Sky all PASS. QR hold 2.53 s (12.6 s, after "Reed-Solomon"); Elevator hold 5.57 s (7.3 s, counterweight explanation).
Visual: Elevator final shot had ~1 s of EMPTY stage after the card (scale only appeared on "a scale"); Sky hook still grazed the brand chip on the punch;
Sky "~1000× smaller" label pushed into captions by the punch; Sky sun half off-screen.
Fixes: QR glide on "error correction"; Elevator push/glide/pull on "It's built"/"plus about"/"rated load"; Elevator scale visible from the first final-shot frame;
Sky punch 1.1→1.08 (y+20), scatter punch 1.32→1.2, molecule 40 px atoms, sun x 1000→960; Elevator shot table fixed (shot 1 at t=0).

## Iteration 3
Automated: Sky all PASS. QR hold 2.23 s at 10.1 s (after repair bytes); Elevator hold 2.43 s at 4.7 s (before "counterweight").
Visual: Elevator count bars pushed off the left edge by the "heavier side" glide; Sky transitions clean.
Fixes: QR glide on "calculated"; Elevator push on "hangs a"; "heavier side" glide x −110 → +60.

## Iteration 4 (full stage rebuild: captions → mix → render → QA via build-episode.sh, all timed)
Elevator + Sky: all PASS. QR hold 2.23 s at 23.5 s (Repair after the H bar). Fix: glide on "a scanner".

## Iterations 5–6 (QR)
it5: hold 2.17 s at 4.7 s (URL label just faded in). Fix: URL now types in character by character across "When the code is generated, your link" + blinking cursor.
it6: QR all PASS.

## Final iteration (QR it7, Elevator it5, Sky it5) — kit fix found by the template smoke test
The template demo (IceDemo) failed the loop check (seam PSNR 20 dB): when the last word ends near the end of the file, its caption and the chapter label
were still on screen in the final frame while frame 0 has neither. Kit fix: captions and the chapter label fade out across the 14 loop frames.
Result: all 3 episodes PASS every automated check; loop seam PSNR rose from ≈34 dB to 48.5 / 49.3 / 50.3 dB (QR / Elevator / Sky).
Visual review of the final transitions/grid sheets: no overlaps with brand/captions/deck, no cross-fades, pills in screen space.
