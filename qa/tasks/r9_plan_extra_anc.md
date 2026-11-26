This is a REVISION pass of an existing, already-built episode. Write the plan by describing the current composition (remotion/src/episodes/ANC.tsx) shot by shot, keeping its look, timing and shot order. Fold in only the changes in the round-9 task below, plus the round-9 rules: atomic text components, one `hero@<spoken phrase>` beat, labels on their words (±0.5 s), the payoff finished 1.5 s before the loop, no artwork cut by a side edge, and <= 3 floating callouts at once. The narration and hooks are fixed.


Round-9 task for this episode:
Targeted revision of the EXISTING ANC composition (remotion/src/episodes/ANC.tsx, last render renders/ANC_v7.mp4). Do NOT rebuild from scratch. Keep the look, shot order and everything that works; follow VIDEO.md.
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
ANC v7 fails these gates (r9 baseline on the v7 render):
1. Clutter: 5 floating callouts at once at 30.8–31.7 s (limit 3). Retire older pills before new ones pop, or merge them into one Badge.
2. Ghost labels at 3.2 s, 21.6 s and 31.0 s (fading text, see rule A). Contrast fails at 42.0 s near the loop seam (ratio 1.26). Labels must stay on solid plates.
3. Entrances: a badge snap at 33.3 s (y 1116–1188).
4. Labels persist: the hook title "THE HEADPHONES THAT FIGHT SOUND WITH SOUND" is readable for only 0.5 s, and "QUIET" is never read in shot 1. Keep them up through their shot on solid plates, or correct shots.md.
5. Label sync: "SPEAKER" is 0.6 s early (16.2 s), "ENGINES" 1.1 s late (27.16 s) and "CUSHIONS BLOCK IT" 0.5 s late (34.56 s).
6. Hero: the critic found no wow moment. Make destructive interference the hero and mark `hero@peak plus valley adds up to flat`. It needs a big centred superposition: the purple noise wave and the yellow anti-noise wave are drawn overlapping, then the sum wave visibly collapses to a flat line, moving for >= 1.5 s.
Known critic weaknesses to fix as they fit:
- Connect the signal path: MIC → CHIP → (flipped) ANTI-NOISE → SPEAKER, with consistent colours throughout.
- Remove the three unexplained grey clouds behind the stage.
- The clap icon must read as clapping hands, and the cushion as an ear cushion.
- Loop seam: the final frame must match frame 0 (same earcup scale, ear not cropped, chapter bar state).
- Hold no static frame for more than 1.75 s (06–09, 12–14 and 21–23 s).
Start with the three key stills (hook / mid / end) and confirm them before the rest.
