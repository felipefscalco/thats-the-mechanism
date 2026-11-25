# Style brief — That's the Mechanism (channel-level, fixed)

Written before code (bang-motion rule #3). Every episode inherits it; an episode brief only fills the "per episode" block.

## Channel
- **Theme:** one everyday thing, opened up to show the hidden mechanism. Editorial engineering-diagram look, not cartoon 3D.
- **Palette:** ink #0D0E12 (base), ink2/ink3 surfaces, paper #F3EFE6 (text), ONE accent amber #FFB020 (current word, reveals, the gear), plus one pillar colour per episode (tech #4CC9F0, engineering #7BD389, physics #9B8CFF, philosophy #FF7AB6). Red #FF5A4E only for failure, green #3DDC97 only for success.
- **Type:** Space Grotesk 700 (display, labels), Inter 900 (captions), JetBrains Mono (data, chapter deck). Text ≥ 30 px on the 1080 stage (enforced by `<Label>`). Max two text levels per shot: one headline + object labels. Captions are a separate track.
- **Background language:** two layers — drifting pillar-colour light + dot grid with slow vertical drift, vignette. Loops exactly (phase = frame / duration).
- **Motion signature:** the gear. It spins in the brand chip, rides the progress rail and stamps the outro card. Transitions are moves of the world (push-through, whip, vertical whip, hard cut + punch), never plain cross-fades.
- **Camera grammar (huashu 镜头语言):** hold while the object moves; slow push 0.6–1.5 s to lead the eye; pull-out to give context/close a section; glide to the next object; punch (0.3 s, +18–32 %) only on reveals; never three pushes in a row.
- **Sound:** voice −14 LUFS; synthesized ambient bed ~−35 LUFS; SFX 10–16 dB under the voice: whoosh on every world move, pop/tick when labels/objects land, glitch/thud/error for failure, confirm for success, riser into the card, signature sting on "That's the mechanism."
- **Structure (per 35–55 s):** hook (object on screen and moving at 0.3 s) → tension → 2–3 mechanism beats → turn → card "THAT'S THE MECHANISM." → 6–10-word callback line → whip back into the hook at frame 0 (exact loop).
- **Special moment per episode:** one real proof on screen (e.g. the QR actually scans).

## Per episode (fill in episodes/<slug>/brief.md)
- Persistent subject (the one object that stays in the world):
- Pillar colour:
- Special moment:
- Shot table: episodes/<slug>/shots.md (lint with scripts/lint_shots.py)
