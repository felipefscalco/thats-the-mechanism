#!/usr/bin/env bash
# Scaffold a new episode from the brand template.
# Usage: scripts/new-episode.sh <slug e.g. 04-ice> <CompositionId e.g. Ice> <pillar tech|eng|sci|philo> "<HOOK TITLE>" ["SOURCE CREDIT"]
# Creates episodes/<slug>/{script.txt,brief.md,shots.md,sources.json,display.json}, remotion/src/episodes/<Id>.tsx,
# registers the composition in remotion/src/Root.tsx. Then: write script.txt -> scripts/build-episode.sh <slug> <Id>
set -euo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"; S="$1"; ID="$2"; PIL="$3"; HOOK="$4"; SRC="${5:-SOURCE}"
E="$P/episodes/$S"; TSX="$P/remotion/src/episodes/$ID.tsx"
[[ -e "$E" || -e "$TSX" ]] && { echo "exists: $E or $TSX"; exit 1; }
N=$(printf "%03d" $(( $(ls -d "$P"/episodes/*/ | wc -l) + 1 )))
mkdir -p "$E"
cat > "$E/script.txt" <<TXT
$HOOK (replace: one-sentence hook the viewer has felt, ≤12 words).

Mechanism, step by step (≈110 words total, 35–50 s at 162–168 wpm).

That's the mechanism.

One-line payoff that loops back into the hook.
TXT
cat > "$E/brief.md" <<TXT
# Style brief — $N $ID  (mandatory before any animation; see docs/STYLE_BRIEF.md)
- Persistent subject (one world for the whole episode):
- Grammar: [3b1b morph | whiteboard build | kinetic type]  — pick one, see docs/STYLE_BRIEF.md#grammars
- Hook frame (visible at 0.3 s, no title card):
- Reveal (the one punch-in moment):
- Palette accent: pillar $PIL + amber; red = failure, green = success
- Two text levels only: LABEL (≥30 px caps) + verdict pill. Captions are separate (84 px).
- Failure list to check in review: docs/ACCEPTANCE.md#style-failures
TXT
cat > "$E/shots.md" <<'TXT'
# Shot table (lint: python3 scripts/lint_shots.py <slug>)
Beats are `kind@phrase`; camera kinds push/pull/glide/punch/settle; others are action beats. A beat every ≤3 s; no fades.

| # | at | shot | subject | beats | on-screen text | in | out |
|---|----|------|---------|-------|----------------|----|-----|
| 1 | `` | Hook | | push@<first words> | | none | push |
| 2 | `That's the mechanism` | Card | channel outro card | sting@That's the mechanism | THAT'S THE MECHANISM. | push | push |
TXT
echo '{"topic": "", "claims": []}' > "$E/sources.json"; echo '[]' > "$E/display.json"
sed -e "s/__SLUG__/$S/g; s/__NAME__/$ID/g; s/__COMP__/$ID/g; s/__PILLAR__/$PIL/g; s/__EP__/$N/g; s/__SOURCE__/$SRC/g; s/__HOOK__/$HOOK/g" "$P/templates/Episode.tsx.tmpl" > "$TSX"
# r8: placeholder captions so the shared Remotion bundle keeps compiling (every other episode's probes/renders) until
# the audio stage writes the real ones; the queue scaffolds episodes long before they have audio.
CJ="$P/remotion/src/$S.captions.json"
[[ -e "$CJ" ]] || echo '[{"text":"(placeholder)","start":0.2,"end":1.0},{"text":"That'"'"'s","start":1.2,"end":1.4},{"text":"the","start":1.4,"end":1.5},{"text":"mechanism.","start":1.5,"end":2.0}]' > "$CJ"
R="$P/remotion/src/Root.tsx"
sed -i "s#// @new-episode-imports#import { ${ID}Video } from \"./episodes/$ID\";\n// @new-episode-imports#" "$R"
sed -i "s#{/\* @new-episode-compositions \*/}#<Composition id=\"$ID\" component={${ID}Video} durationInFrames={frames((durations as Record<string, number>)[\"$S\"] ?? 10)} {...portrait} />\n    {/* @new-episode-compositions */}#" "$R"
echo "created $E and $TSX (#$N). Next: edit script.txt, then scripts/build-episode.sh $S $ID"
