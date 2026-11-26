You are the BUILDER of composition `{ID}` (repository: {ROOT}), doing a self-review before an independent critic sees it.
Open these images: the contact sheet {SHEET} (one still every 1.5 s, left-to-right, top-to-bottom) and the key stills {KEYS}
(hook / mid / end). Compare them with the frozen plan episodes/{SLUG}/VIDEO.md (read it).
Check, honestly: does each shot read as ONE continuous world (not a slide deck)? Is the hook the subject at frame 0? Any text
cramped, clipped, overlapping or low-contrast? More than 3 callouts at once? Dead holds? Does the end match frame 0?
If you find real problems, fix them in remotion/src/episodes/{ID}.tsx only (same rules as before; no full renders; run tsc),
then re-run: .venv-tts/bin/python scripts/preview.py {ID} {SLUG} {N}
Reply with JSON: {"issues_found": [..], "changed": true|false, "confidence_ship": 1-5}
