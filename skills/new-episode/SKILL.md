---
name: new-episode
description: Scaffold a new That's the Mechanism Short — folder, brief, shot table, Remotion composition from the official template, and Root.tsx registration. Use when starting a new episode, adding a slug, or the user says "new short", "new episode", or "scaffold".
---

# new-episode

Create the files for one episode, then stop for **human approval of the angle** before writing the full script (that is `script-and-factcheck`).

## Command

```bash
scripts/new-episode.sh <slug> <CompId> <pillar> "HOOK TITLE" "SOURCE"
# slug:     05-short-kebab   (zero-padded number + kebab-case)
# CompId:   PascalCase React composition id, e.g. QrLogo
# pillar:   tech | sci | eng | philo     (maps to PILLARS in remotion/src/brand/tokens.ts)
# HOOK:     short on-screen hook title
# SOURCE:   short attribution shown in the tag line, e.g. "DENSO WAVE"
```

The script should:

1. Create `episodes/<slug>/` with `brief.md`, `script.txt` (placeholder), `shots.md`, `sources.json`.
2. Copy `templates/Episode.tsx.tmpl` to `remotion/src/episodes/<CompId>.tsx` and fill slug, id, pillar, hook.
3. Register the composition in `remotion/src/Root.tsx` (import + `<Composition>`).
4. Leave a duration key in `remotion/src/durations.json` (updated for real after mix).

If `new-episode.sh` already does these steps, run it rather than inventing a parallel scaffold. Then fill `brief.md` with the per-episode block from `docs/STYLE_BRIEF.md`:

- Persistent subject (the one object that stays in the world)
- Pillar colour
- Special moment (a real proof that will appear on screen)
- A one-sentence angle for human approval

## Rules

- Do not start TTS, animation, or rendering until the angle is approved and the script is approved.
- Do not reuse `IceDemo` as a shippable episode; it is a smoke test of the template.
- Keep numbering monotonic with existing folders (`01-qr-code`, `02-elevator`, `03-sky`, …).
