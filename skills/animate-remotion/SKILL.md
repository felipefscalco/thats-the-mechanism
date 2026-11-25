---
name: animate-remotion
description: Build or edit a That's the Mechanism Remotion composition using the shared brand kit, template, safe zones, and camera grammar. Use when writing episode TSX, fixing layout, motion, loops, or typography, or when the user mentions Remotion, shots, or the visual.
---

# animate-remotion

All animation is original Remotion (React → MP4). Do not generate video with an AI video model and drop it in. Do not use stock b-roll.

## Where things live

| Path | Role |
|---|---|
| `remotion/src/brand/` | `EpisodeShell`, `Shot`, `Kit` (`Label`, `Pill`, `Stage`), `Gear`, `Sfx`, `timing`, `tokens` (palette, fonts, `LAYOUT` safe zones) |
| `templates/Episode.tsx.tmpl` | Starting composition — copy via `new-episode.sh`, then replace the placeholder subject |
| `remotion/src/episodes/<CompId>.tsx` | This episode only |
| `remotion/src/Root.tsx` | Composition registry |
| `remotion/src/<slug>.captions.json` | Word times |
| `remotion/src/durations.json` | Audio duration per slug (written after mix) |
| `remotion/.agents/skills/` | Official Remotion agent skills (best practices, captions, render, license) |

## How to build a composition

1. Wrap the episode in `EpisodeShell` (intro sting over the hook, captions, chapter deck, outro card, exact loop).
2. Each scene is a `Shot` with a world-move transition (`push-through`, `whip`, `whipUp`, `cut+punch`) and a camera (`push`, `pull`, `glide`, `punch`, `settle`).
3. Put verdict pills in the Shot `hud` (screen space) so a camera move cannot shove them under the brand chip or into captions.
4. Drive cue times with `makeAt(words)("phrase from the script")` — it throws if the phrase was not spoken. Do not hard-code frame numbers for dialogue beats.
5. Place SFX with `<Sfx cue={...} name="pop" />` (or `cue(frame, "pop")`) on visible events. See `skills/sfx-mix`.
6. `<Label>` refuses to render below 30 px. Keep stage text to two levels. ≤8 words per label (lint).
7. The last ~14 frames must whip back to the hook at frame 0. The shell fades captions and the chapter label across those frames so the loop seams. Do not put unique end-card text that is still visible on the last frame unless it also exists on frame 0.

## Safe zones (1080×1920)

- Brand chip / tag: y < 290
- Stage (content): y 290–1190
- Captions: y 1222–1440
- Chapter deck: y 1462–1552
- Keep clear: y > 1560, and x > 900 when y > 900 (platform UI)

## Camera and motion grammar

- Subject on screen and moving at 0.3 s; visible change by 1.0 s.
- Something happens at least every 2 s (no dead stage holds).
- Slow push 0.6–1.5 s to lead the eye; punch 0.3 s (+18–32 %) only on reveals; never three pushes in a row.
- No cross-fades between sections.
- Editorial diagram look — not a slideshow, not cartoon 3D unless a human later changes the style brief.

## Check as you go

```bash
python3 scripts/lint_shots.py <slug>
(cd remotion && npx tsc --noEmit -p .)
# then render + QA via skills/qa-loop
```

Official Remotion guidance in `remotion/.agents/skills/` still applies (sequences, `useCurrentFrame`, no invalid hooks). This skill wins on channel-specific layout and motion rules.
