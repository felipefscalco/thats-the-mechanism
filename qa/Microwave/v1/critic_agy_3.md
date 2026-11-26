# Critic (Antigravity gemini-4-neon-high, evidence=video) — Microwave v1

# Calibrated Critic — Microwave (v1)

- **File:** `renders/Microwave_v1.mp4`
- **Model:** `agy:gemini-4-neon-high` · samples 1 · free tier `$0.00`
- **Overall (weighted, weakest-link capped):** **5.06 / 10** · verdict **ONE MORE PASS**
- **Generated:** 2026-11-26T00:56:41-03:00

## Weaknesses (listed before scoring)
- **[00:16.0] (blocker · clarity / concept_wow)** The actual scale mechanism is never visually shown: `ONE HOLE` flashes for < 0.5 s at 00:16.0 before cutting away, the side-on screen holes (00:16.5-00:28.5) are drawn wider than the purple wave stroke so the wave visually looks like it should pass through, and at 00:25.0-00:28.5 the top and bottom yellow light rays pass directly through solid gray metal bars instead of the holes. — *fix:* Replace 00:15.0-00:24.0 with a hero 48-frame exponential scale-zoom (`cubic-bezier(0.22, 1, 0.36, 1)`): show a bold 12 cm amber `#FFB020` wave crest spanning 60+ tiny 1.5 mm holes (paired with a real macro photo ProofCard of a microwave mesh door), then push the camera through a single hole into a true-to-scale cutaway where the mesh gaps are 12 px, the microwave is a 180 px tall translucent `#9B8CFF` wavefront envelope that physically rebounds with squash/overshoot, and 3 px light rays thread strictly through open gaps without ever touching solid metal bars.
- **[00:38.0] (blocker · design_typography)** Severe label collisions: `SEES A WALL` lands directly on top of and obscures `MICROWAVE · ≈ 12 cm` (00:38.0-00:40.0), `METAL SCREEN` overlaps the top row of mesh holes (00:08.0-00:10.0), and the opening headline's black backing box clips the microwave's top-left corner (00:00.5-00:05.0). — *fix:* Reserve dedicated non-overlapping layout lanes with >= 24 px clearance: place `SEES A WALL` and `SEES A WINDOW` in a top callout band at y = 320 px above the cutaway box (moved to y = 420 px); lift `METAL SCREEN` 36 px above the mesh frame to y = 380 px; and raise the opening headline above y = 380 px without an opaque clipping rectangle while shifting the microwave down 40 px.
- **[00:45.5] (blocker · loop)** Broken loop seam and unsettled opening frame: at 00:45.5-00:46.0 the closing horizontal whip only slides ~70% across, clipping the timer at `0:3` and mismatching 00:00.0, while 00:00.0 itself starts awkwardly zoomed/cropped on the right edge before snapping into center by 00:00.5. — *fix:* Set frame 0 (00:00.0) to the fully centered hero microwave pose (880 px wide at x = 540 px, `0:30` fully framed with 100 px margins), add a 12-frame micro-push (`scale 1.0 -> 1.03 -> 1.0`, spring damping 14) for immediate 0-1 s motion, and lock the final 14 frames (00:45.5-00:46.0) to a full 1080 px `easeInOutQuint` whip-pan that lands pixel-identically on frame 0.
- **[00:29.5] (major · concept_wow / style_fidelity)** Template slide-deck feel and empty stage: 00:29.5-00:32.0 leaves 70% of the canvas empty beside an unidentifiable featureless beige slab and irrelevant stock spinning gears, followed by an unreadable tiny lollipop icon (00:34.5), while the exact same flat brown cutaway + clipart eye repeats verbatim across three scenes (04/07, 05/07, 07/07). — *fix:* Remove the off-theme spinning gears wallpaper (replace with faint 4% opacity `#F3EFE6` RF blueprint ticks), redesign 06/07 as a detailed 340 px side-profile microwave housing with door latch and an animated flat-vector handheld RF meter whose needle/bar peaks at `5 mW/cm²` across a bold 300 px `2 in / 5 cm` ruler, and re-stage 07/07 as a split-screen dual-lens view (wave view vs human view) rather than repeating the 04/07 slide.
- **[00:17.5] (major · motion_craft)** Multiple static holds > 2 s (00:00.5-00:04.5, 00:06.5-00:09.0, 00:17.5-00:20.0, 00:29.5-00:32.0) combined with linear/abrupt pop-in entries (`SOLID METAL TO IT` at 00:20.0, `LIGHT SLIPS THROUGH` at 00:28.0, `US FEDERAL LIMIT` at 00:30.5, all hole rings firing simultaneously at 00:09.5) with zero anticipation, stagger, or overshoot. — *fix:* Keep continuous meaningful physical motion on stage every <= 1.5 s (pulsing standing waves inside the opening microwave window; a 2-frame diagonal cascade stagger across the mesh holes at 00:08.5-00:09.8 with scale `0.85 -> 1.12 -> 1.0` over 10 frames; continuous wave bounce ripples into the mug) and replace every pill/icon pop with a 12-frame spring entry (`translateY 24 px -> -4 px -> 0 px`, scale `0.9 -> 1.04 -> 1.0`).
- **[00:18.5] (major · design_typography)** Multiple diagram labels are squint-inducing (< 30 px on 1080-wide stage) and low-contrast (automated QA `min_ratio=1.18`), including `THE SCREEN, SIDE-ON`, `OUTSIDE`, `INSIDE`, `MICROWAVE · ≈ 12 cm`, `LIGHT · < 1 µm`, `21 CFR 1030.10 · US FDA`, `2 in · 5 cm`, `ONE HOLE`, and `SEES A WALL`/`SEES A WINDOW`. — *fix:* Enforce a strict 32 px minimum font size (Space Grotesk Bold / JetBrains Mono Medium) across every on-stage callout, raise muted gray label color to `#D8D4CC` (>= 10:1 contrast on `#0D0E12`), and give all pill badges 34 px text with at least 14 px vertical and 24 px horizontal padding.
- **[00:42.0] (major · sound_sync)** Sparse, generic synthetic UI plinks and breathy whooshes fail to sell the physical object; most glaringly, when the microwave timer hits `0:00` at 00:42.0 there is no classic microwave *ding*. — *fix:* Replace generic UI tones with layered physical foley at -12 to -16 dB under VO: a subtle 60 Hz cavity hum + turntable whir during 00:00-00:05, a crisp metallic sheet ping on the 00:07.5 screen reveal, a resonant low-pass wave bounce thump (120 Hz -> 55 Hz) locked to the exact reflection frame at 00:21.2, a crystalline shimmer as light threads the holes at 00:24.5, and a bright metallic microwave bell *ding* locked to `0:00` at 00:42.0.
- **[00:15.0] (major · voice_captions)** Highlighted caption words collide with neighbors (`themicrowaves` at 00:04.0, `centimetreslong.` at 00:15.0, `windowfor` at 00:43.5), orphan single words hang on second lines (`a`, `into`, `oven.`), `2.45 GHz.` never highlights amber (00:11.5-00:13.0), and metronomic ~0.7 s VO pauses between every sentence sap Shorts pacing. — *fix:* Eliminate inline word scaling on active captions (or enforce a fixed `0.32em` flex gap) so highlighted words never collide, balance caption line breaks to eliminate 1-word orphans, bind `2.45 GHz.` to the active amber highlighter, and tighten inter-sentence VO pauses from ~700 ms down to 220-320 ms (reserving a 450 ms beat only before "That's the mechanism.").
- **[00:29.0] (minor · finish_texture)** Sterile flat textures and unmasked blur transitions: the metal mesh (00:07.5) reads as tan dots on a plain dark gray card, the oven cavity (00:16.5) is a flat muddy brown box, and the whip-up transition at 00:29.0 smears green pills directly over the top brand chip. — *fix:* Render the metal plate in brushed steel `#2B303A` with 2 px `#454D5C` rim highlights and inner hole shadows, add clean vector cavity ribbing + a warm amber lamp cone inside the cutaway, and clip all stage transitions to the y = 260-1190 px viewport mask so motion blur never bleeds across persistent UI chrome.
- **[00:00.5] (minor · hook)** The opening 5 seconds barely visualize the hook question ("So why do the microwaves stay in?"): only a tiny mug rotates slowly until a brief 0.5 s purple window outline blinks at 00:04.5. — *fix:* From frame 12 (00:00.4), animate translucent `#9B8CFF` standing-wave arcs pulsing and rebounding off the inside of the door mesh while warm `#FFB020` light streaks shine outward toward the viewer, visually staging the paradox within the first second.

## Gaps vs reference channels
- Jared Owen: Instead of continuous physical motion and camera choreography showing how parts interact in space, this film cuts between rigid 2D schematic slides with static 2.5-4 s holds and a clipart eye floating in black space.
- Animagraffs: Whereas Animagraffs delivers dense mechanical accuracy and impeccably spaced callouts, here the side-on mesh holes are wildly out of scale with the 12 cm wave, light rays clip through solid metal bars, and labels collide directly over diagram geometry and other text.
- The Why Side: While The Why Side pairs punchy VO pacing with a bold visual-state change every 2-4 s, this cut drags through metronomic ~0.7 s sentence pauses, repeats the same brown box cutaway three times, and leaves 70% of the stage empty during the 00:29.5-00:32.0 regulation beat.
- mg-styles-15 Flat Vector (7.6 anchor): Compared to the anchor's springy anticipation-overshoot-settle entries, 2-4 frame staggers, and shape-driven transitions, every pill, ring, and icon here pops or fades linearly between blurry whip cuts, putting motion craft and style fidelity well below 7.6.

## Strengths
- Clean, readable color-coded contrast between purple microwaves (#9B8CFF) and warm yellow light rays (#FFB020/#F3EFE6) in the side-on comparison.
- Clear, structured narrative arc with a crisp opening question and memorable closing contrast ("a wall for microwaves, a window for you").
- Consistent brand framing (top chrome, chapter progress deck, end card) with intelligible narration that stays cleanly above the SFX bed.

## Caps triggered
- Stage visually static for > 2 s (00:00.5-00:04.5, 00:06.5-00:09.0, 00:17.5-00:20.0, 00:29.5-00:32.0) -> motion_craft <= 6
- Elements pop/fade in without anticipation, easing, stagger, or overshoot (00:09.5, 00:16.0, 00:20.0, 00:28.0, 00:30.5, 00:34.5, 00:38.0) -> motion_craft <= 6
- Generic template/slide-deck look (spinning gears wallpaper, clipart eye, untextured beige slab, repeated brown box diagram) -> style_fidelity <= 6 and concept_wow <= 6
- Sub-30 px low-contrast diagram labels and direct label collisions (00:08.0 METAL SCREEN on holes, 00:38.0 SEES A WALL obscuring MICROWAVE · ≈ 12 cm) -> design_typography <= 6
- Core scale mechanism cannot be understood from the picture alone with sound off (00:16.0 ONE HOLE flashes < 0.5 s; side-on holes drawn wider than wave stroke; light rays clip solid metal dashes) -> clarity <= 6
- Repetitive generic synthetic UI plinks/whooshes lacking tactile diegetic foley (missed 0:00 microwave ding at 00:42.0) -> sound_sync <= 6
- Ending whip fails to land cleanly on frame 0 and frame 0 starts cropped/unsettled (00:45.5-00:46.0 vs 00:00.0-00:00.5) -> loop <= 5

## Scores
| Dimension | Score |
|---|---:|
| hook | 6 |
| clarity | 5 |
| motion_craft | 5 |
| design_typography | 5 |
| concept_wow | 4 |
| style_fidelity | 5 |
| finish_texture | 5 |
| sound_sync | 5 |
| voice_captions | 6 |
| loop | 4 |

## Summary
Microwave_v1 is a clean template-grade draft that conveys the premise verbally, but fails as a visual motion-design Short: the core scale mechanism (12 cm wave vs ~1.5 mm mesh hole vs < 1 µm light) is never visually proven (ONE HOLE flashes < 0.5 s and light rays clip through solid metal dashes), labels collide at 00:08.0 and 00:38.0, multiple beats sit static for 2.5-4 s, the sound design misses obvious physical microwave foley including a 0:00 ding, and the closing whip misses frame 0. Requires another full craft pass before shipping.
