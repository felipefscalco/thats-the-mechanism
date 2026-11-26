Targeted revision of the EXISTING Elevator composition (remotion/src/episodes/Elevator.tsx = v6b, last render renders/Elevator_v6b.mp4). Do NOT rebuild from scratch. Keep the look, shot order and everything that works; follow VIDEO.md.
Round-9 rules (all measured by the gates; the preview loop shows every failure):
A. Text is ATOMIC. Use only Label / TagLabel / Badge / Pill / TitleHook from ../brand. Raw SVG <text>/<tspan> fails the static gate.
   The `o` prop is entrance progress (scale pop), not opacity. Never put text inside a parent whose `opacity` fades, because that is
   the see-through "ghost text" the critic flagged and the contrast gate fails. Show or hide a text group with a binary switch or
   with o (scale), never with a fade.
B. Hero beat. In shots.md, mark the ONE wow moment as a beat `hero@<exact spoken phrase>`. From that word until the next shot or
   card, the hero subject must:
   - be big (bounding box >= 35 % of the stage) and centred (|dx| <= 15 %, |dy| <= 20 %);
   - visibly move (no still > 1.0 s);
   - last >= 1.5 s;
   - not be cut by a side edge.
C. Label timing. Every on-screen label that echoes spoken words must appear within ±0.5 s of the word. Time pops to the caption
   word times in episodes/<slug>/captions.json, not to round numbers. Use `LABEL @spoken phrase` in shots.md when the label
   paraphrases the voice.
D. Payoff hold. EpisodeShell freezes the final 1.5 s before the loop seam. Every payoff animation must be complete by then.
E. Framing. Artwork must never be cut by a side edge (the art-edge gate fails >= 0.6 s). Keep >= 24 px of side margin. Shift the
   camera or shrink the art instead of pushing it off-frame. Thin beams entering from off-screen are fine.
F. Clutter. At most 3 floating callouts (pills/badges) on screen at once, held >= 0.6 s.
G. Keep the narration, the captions and the audio exactly as they are. The hooks stay as they are (owner decision).
Keep every row of episodes/<slug>/shots.md true to what you draw (labels, timings, hero beat).
Elevator v6b fails these gates (r9 baseline on the v6b render):
1. Motion holds of 2.4 s at 24.6 s and 2.2 s at 22.3 s. Add real beats.
2. Contrast: many labels are < 4.5:1 (min 1.09), e.g. at 0–4 s, 14–25 s and the L-floor ticks on cream. Put every label on a dark plate (Label/Badge with a backing).
3. Ghost labels at 17.0 s and 34.0 s (y 1106–1162).
4. Safe zone: the "= EMPTY CAR" / "+ 40-50% LOAD" pills at x 654–950, y 908–970 (10.4 s on) fall in the right-side UI, and the 0.2 s top-right label at x 946–1080 is at the edge. Keep >= 24 px from edges and clear of the right action rail.
5. Clearance: the hook title occludes the shaft or sheave artwork at 0–4.2 s. Give it >= 36 px of clearance (move the title or the art; do NOT change the hook wording).
6. Entrances: hand-rolled badge snaps at 1.07 s and 2.4 s (MOTOR badge), and element snaps at 17.2 s and 18.4 s. Use TagLabel/Badge/<Enter>.
7. Label sync: "≈ BALANCED" is 0.6 s early (3.58 s), "COUNTERWEIGHT" 2.0 s early (6.86 s) and "= EMPTY CAR" ~1 s early (9.16 s). Pop each label on its word.
8. Sound-off clarity: add a DIFFERENCE keyword at "It only fights the difference." (16.24 s).
9. Hero: mark `hero@It would rise`. The empty car rising after BRAKE OFF must be big (>= 35 % of the stage), centred and moving for >= 1.5 s. Zoom or cut to it, and do not leave it as a small move inside the distant box (v6b's measured hero lasts only 1.36 s).
Lessons from the rejected v7 candidate (branch r8-elevator-v7-candidate): its preview fixes were good, but it lost readable CAR/CW and MOTOR labels and pushed the shaft off the left edge at 11–14 s to make room for pills. Do neither: keep labels persistent, and shrink or reposition rather than crop.
Known critic weaknesses to fix as they fit:
- 81 % of the film sits on one unchanging schematic box. Vary the framing with camera pushes/glides to the motor, the counterweight and the car.
- Show force arrows (gravity on car vs counterweight, the motor's small torque) for "only fights the difference".
- After BRAKE OFF, there must be no frozen 2 s; the motion must start on the word.
- The bar-chart CAR/CW headers must sit over their columns at >= 30 px.
- Remove the two unexplained dark rails outside the shaft.
- Photo credits must be >= 30 px.
Start with the three key stills (hook / mid / end) and confirm them before the rest.
