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

## Round 4 additions
- **Style-frames gate:** for a new look, render stills (`node remotion/style_frames.mjs`, `scripts/style_sheet.py`) into `style_frames/` and get the owner's pick before animating.
- **Title-as-hook:** `<TitleHook t={[…]} />` (dark backing card) over a scale reveal: frame 0 is a bright close-up of the subject, pulling out to the whole mechanism within ~1 s.
- **Backdrops:** `EpisodeShell backdrop="library/<name>.jpg" backdropDim={…}` for drawn backgrounds (`assets/library/backdrops/make_backdrops.py`); keep them away from dense mechanisms.
- **ProofCard:** `<ProofCard src="photos/…" tag credit focus focusLabel startFrame duration />` for 1–2 s of a licensed real photo (credit line in MONO ≥ 30 px).
- **Motion:** smooth keyed trajectories with cubic in-out and back-overshoot on reveals; coupled secondary motion (cables, counterweight, wheels) from the same variable.
- **Probe mode:** labels honour `PROBE` (`--props '{"probe":true}'`) for the contrast check; don't hard-code text colours outside `<Label>`/`<Pill>` when it can be avoided.

## Round-5 motion grammar (emilkowalski/skills MIT, mg-styles-15 Flat Vector MIT, video-shotcraft Apache-2.0, motion-video-kit MIT)
- Easing tokens in `brand/timing.ts`: `EASE.OUT` (0.23,1,0.32,1) for entries/responses, `EASE.IN_OUT` (0.77,0,0.175,1) for on-screen moves, `EASE.OVERSHOOT` (0.34,1.56,0.64,1) for flat-vector landings, `EASE.EXIT` only for exits. Never ease-in an arrival.
- Never `scale(0)`: use `popScale(p)` (0.62 → overshoot → 1) with `popOpacity(p)`. Large cards (ProofCard) enter from 0.94 + 40 px rise, no spring wobble; inner photo lags 3 f.
- Stagger with `stagger(i)` (shrinking delays, 2–4 f); one hero moving at a time; `squash()` ~10 % on landings.
- Camera `punch` = shotcraft crash-zoom: 5 f anticipation pull-back, 5 f push, 4 f recoil; its stamp/glint SFX land on the hit frame (+7 f).
- A visual-state change every ≤4 s (qa.py cadence); hooks open on ONE subject; text that sits on art uses `TagLabel` (backing).
- Finish: static procedural grain (7 % overlay) from `scripts/make_grain.py`; `--props '{"grain":"anim"}'` costs +30 % render.
