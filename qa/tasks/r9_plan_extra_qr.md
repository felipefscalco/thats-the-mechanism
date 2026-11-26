This is a REVISION pass of an existing, already-built episode. Write the plan by describing the current composition (remotion/src/episodes/QR.tsx) shot by shot, keeping its look, timing and shot order. Fold in only the changes in the round-9 task below, plus the round-9 rules: atomic text components, one `hero@<spoken phrase>` beat, labels on their words (±0.5 s), the payoff finished 1.5 s before the loop, no artwork cut by a side edge, and <= 3 floating callouts at once. The narration and hooks are fixed.


Round-9 task for this episode:
Targeted revision of the EXISTING QR composition (remotion/src/episodes/QR.tsx, last render renders/QR_v6.mp4). Do NOT rebuild from scratch. Keep the look, shot order and everything that works; follow VIDEO.md.
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
QR v6 fails these gates (r9 baseline on the v6 render):
1. Motion: change at least every 1.75 s. v6 holds 3.5 s at 30.6 s, 2.8 s at 45.1, 2.8 s at 24.8, 2.4 s at 5.5, 2.4 s at 35.9 and 2.3 s at 19.4. Add real beats inside each hold (module flips, a scan sweep, a camera glide, a counter).
2. Entrances: a snap at 43.8 s (tall element x 315–380), a badge snap at 43.4 s, and an opacity-only fade at 15.1 s. Use <Enter> / TagLabel pops.
3. Safe zone: a label at x 892–936, y 950–994 (10.6–11.2 s) sits inside the right-side Shorts UI. Move it inward (>= 24 px from edges, clear of the right action rail).
4. Labels persist: the hook title "THE CODE THAT REPAIRS ITSELF" is readable for only 0.5 s (it must stay through its shot or be dropped from shots.md). "NO SCAN" is never readable in shot 5; draw it large on a solid plate.
5. Label sync: "DATA" appears 3.8 s before "data" is spoken (11.88 s), and "SPARE PARTS INCLUDED" appears 0.8 s early (51.32 s). Pop them on their words.
6. Sound-off clarity: add on-screen keywords for "Glare and scratches spend the same budget." (38.3 s, e.g. GLARE + SCRATCHES eating the same 30 % bar) and "cover one of the three big corner squares" (41.1 s, e.g. CORNER SQUARE = FINDER).
7. Hero: mark `hero@restore about thirty percent` (or the repair moment you make strongest). Make it a big centred QR whose missing modules are rebuilt by visible parity arcs, moving for >= 1.5 s.
Known critic weaknesses to fix as they fit: the 30 % damage mask must never cover the three finder squares (they are the 'game over' beat); the reconstruction must show repair bytes flying into the gaps rather than a static grid; and avoid repeating the same centred QR framing for long stretches.
Start with the three key stills (hook / mid / end) and confirm them before the rest.
