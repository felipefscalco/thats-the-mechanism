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
