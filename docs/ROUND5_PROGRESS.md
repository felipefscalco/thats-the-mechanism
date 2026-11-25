# Round 5 progress (resume file)
Updated: 2026-11-25 ~20:00 BRT. Step 1 (repo sync) DONE: 45ed8c5..1718c89 pushed. Round 5 is NOT pushed.

## Done
- Licences verified at source → docs/ASSET_LICENSES_R5.csv (UISFX CC0 audio; Mixkit SFX licence forbids raw redistribution → not in repo;
  Texturelabs terms forbid sharing → own grain; Open Peeps/Open Doodles/3dicons CC0; unDraw/ManyPixels custom; Flowbite/Phosphor MIT).
- Assets: 4 UISFX cues (latch/detent/land/step) in remotion/public/sfx + sfx/uisfx + CREDITS.csv; 60 Phosphor icons in assets/library/icons/phosphor;
  procedural grain scripts/make_grain.py → remotion/public/grain (static by default; animated +30% render, +33% size).
- Kit: EASE tokens/popScale/popOpacity/stagger/squash (timing.ts); Pill + all scale(pop) never start at 0; Shot punch = shotcraft crash-zoom
  (anticipation pull-back → push → recoil, SFX on the hit frame); ProofCard eased entry, safe-zone geometry (W 760, x 100), `treat` prop;
  TagLabel (label on backing); FlatPlanet (Sky, replaces three.js planet); Grain overlay in EpisodeShell; riser moved to at-47 (silence beat).
- Episodes: Sky single-subject hook (sunset only, noon drops in on "Both"), molecule shrink + glide, 2-line ~1000× label, TagLabels;
  Elevator graded HABS photo, CAR/L-labels 30 px, cadence punches (fights the difference, nearly empty), cascading rise chevrons;
  QR cadence punch at "cut into bytes", byte modules popScale, REBUILDABLE 42 px, REPAIR BUDGET left-anchored, title fades before push.
- Audio: mix_one.sh ducks the bed 0.42 s before "That's the mechanism" (remixed public wavs).
- QA (qa.py/contrast.py): raw SVG/CSS fontSize<30 gate; cadence (state change ≤4 s, diff≥10); pre-catchphrase silence ≤−38 dBFS;
  Shorts safe zones (held ≥0.6 s).
- Gates: pipeline.config.json, scripts/gates.py (human/auto/off + logged env override), approvals/approvals.jsonl (backfilled Felipe decisions),
  scripts/facts.py + episodes/*/facts.json (all PASS; negative test FAILs), tts.py refuses on facts/script gate, scripts/storyboard.py, scripts/ledger.py.
- Critic: --mode calibrated (anchored scale, weaknesses first, caps, refs, Flat Vector contact-sheet anchor, measured QA), --verify, --samples,
  --compare (pairwise). Results in qa/calibration/.

## Calibration findings so far
- legacy (r4 prompt): v3 9.2 / v4 9.3 (3-flash-preview); v3 8.0 on 3.8-flash.
- calibrated absolute: v3 5.86 (3.8-flash), v3 6.46 (3-flash-preview), v4 6.06 (3-flash-preview) → absolute scores still do NOT rank v4>v3 reliably.
- pairwise A=v3 B=v4: prefers v4, strength 3/3, high confidence (3.8-flash). Swap-order run timed out → rerun.
- Flat Vector reference scored 5.0 (landscape/no VO penalised) → reference-film anchoring is weak.
- gemini-3.1-pro-preview: free-tier 429 every time; 3.8-flash often 503.

## v5 iteration status
- it1: all render; fails = safe zones (QR, Elevator), cadence (QR, Elevator), Sky contrast (false: code edited mid-batch, L-24).
- it2: QR safe zone (title fling at 5.0 s, REPAIR label) → fixed in code; Elevator cadence 14.8 s → fixed; Sky hold/contrast/safe zone → TODO inspect.
## Next
1. Inspect Sky it2 failures, fix. 2. Render it3 all three. 3. Pairwise critic v4→v5 per episode + calibrated absolute on v5; verify round.
4. LESSONS L-22+, BACKLOG, METRICS, TESTS_R5.md, critic SKILL, AGENTS/README r5 sections, contact_sheet_v5. Do NOT push.

## Update (it3 running, compare2 done) — 20:03 BRT
- compare2: swap test cmp_A-v4_B-v3 → prefers A=v4 (strength 2, margin −0.85); cmp_A-v3_B-v4 on 3-flash-preview → prefers B=v4 (+1.76). Pairwise is position-robust: v4 > v3 both orders.
- elev_v4_cal2 FAILED: 3-flash-preview 429 quota + 3.8-flash 503. Free-tier daily quota may be exhausted → critic v5 runs may need to wait.
- QR it3: ALL PASS (cadence 3.8 s, beat −88.8 dB, safe zones clean).
- Skills updated: critic, qa-loop, script-and-factcheck, animate-remotion.

## Update — 20:35 BRT: v5 DONE (pending strong critic only)
- it3: QR + Elevator ALL PASS (15/15). Sky it3 failed hold 2.23 s (ISS photo) + safe zone (Rayleigh formula pushed right by punch) →
  added "BLUE SCATTERED AWAY" pill at "scattered out", formula 52 px, punch s1.14 x−20 → **Sky it4 ALL PASS**.
- Final: renders/{QR,Elevator,Sky}_v5.mp4 (QR it3, Elevator it3, Sky it4). contact_sheet_v5.{png,jpg}. Storyboards qa/*/v5/storyboard.jpg.
- Gemini: 3-flash-preview and 3.8-flash daily free quota exhausted (20/day, retry about 8.8 h). v5 critic ran on 3.1-flash-lite-preview
  (validated on v3/v4 in both orders). Lite pairwise v4→v5: QR tie ("identical"), Elevator v5 (s3, +0.15), Sky v5 (s1, +0.65).
  Lite calibrated v4→v5: QR 6.3→6.5, Elevator 6.7→6.7, Sky 6.5→6.5. Lite legacy v5: 8.9 / 8.3 / 9.5.
- TODO after reset: `_scratch/critic_v5_strong.sh` (9 calls: pairwise, calibrated, verify).
- Docs done: LESSONS L-21 update + L-22..L-27, BACKLOG, TESTS_R5.md, METRICS regen, skills (critic, qa-loop, script-and-factcheck, animate-remotion), README/AGENTS r5.
- Not pushed.
