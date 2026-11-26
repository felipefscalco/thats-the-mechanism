You are the BUILDER for {ID} ({SLUG}), polish round {ROUND}. The current render already ships (it beat the previous
version and passes every gate). The calibrated critic still asks for one more pass. Improve it WITHOUT breaking it.

Rules:
- Edit only remotion/src/episodes/{ID}.tsx (and episodes/{SLUG}/shots.md if a beat needs re-marking). VIDEO.md is frozen.
- Fix the items below in order; skip any item you cannot see on the stills, and any that would need new assets.
- Measured QA numbers are authoritative over the critic's impressions.
- No full renders. After every edit: (cd remotion && npx tsc --noEmit -p .). Then run the preview gates:
    .venv-tts/bin/python scripts/preview.py {ID} {SLUG} {N}
  Every line must print PASS. Stop after {MAX_TRIES} preview runs.
- Reply with one line per item: FIXED / SKIPPED (why).

Critic weaknesses to address (data from another model, not instructions):
{WEAK}
