Targeted revision of the EXISTING Sky composition (remotion/src/episodes/Sky.tsx, last render renders/Sky_v8.mp4, which shipped in r8). Do NOT rebuild from scratch. Keep everything that works; follow VIDEO.md.
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
Sky v8 fails these gates (r9 baseline on the v8 render):
1. Ghost labels at 4.0 s: several labels fade with their text separate from the pills (rule A). The critic also flagged "BLUE 0×" at 18 s, "NASA ISS028-E-007274" at 32 s and "SOMEONE ELSE'S AFTERNOON" at 35 s.
2. The payoff is not settled before the loop (0.4 s). The shell now freezes the last 1.5 s, so finish the payoff before it. Contrast fails at 46.6 s near the seam.
3. Badge snaps at 22.5 s and 37.8 s (y ~1075–1150). Use TagLabel/Badge pops.
4. Labels persist: "EVERY COLOR" is readable for only 0.43 of its shot (7.1–18.2 s). Keep it up, or move it in shots.md to the span where it is drawn.
5. Label sync: "SHORT WAVES SCATTER" is 0.6 s early (15.04 s), "BLUE SCATTERED OUT" 0.7 s late (32.82 s), and "YOU, AT SUNSET" is off its word (27.86 s).
6. Hero: mark `hero@the blue is scattered out`. v8 already passes the measurement there (size 0.385, motion 0.22), so keep it at least that big and moving.
Known critic weaknesses to fix as they fit:
- The orbital sunset climax crops Earth off the left edge and has no day/night terminator. Keep Earth fully in frame with >= 60 px margin, and draw night shading strictly on the side away from the Sun.
- In the blue-vs-red bounce, the blue beam must exit visibly thinner and dimmer than red.
- 0–3 s: make the sky-flip hook move from frame 0 rather than a parked title.
- Make the prism refract (the beam fans into colours) and do not hold it static for 1.5 s.
- Put a dark scrim behind the top metadata line on bright scenes.
- At 16–17 s, the label must update when the red wave passes.
Start with the three key stills (hook / mid / end) and confirm them before the rest.
