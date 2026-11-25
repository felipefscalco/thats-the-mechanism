---
name: script-and-factcheck
description: Write a 35–55 s That's the Mechanism voiceover and shot list, and fact-check every claim with at least two sources. Use when drafting or revising a script, hook, sources.json, or shots.md.
---

# script-and-factcheck

Turn an approved angle into a spoken script, a sourced claim list, and a shot table. Then **stop for human approval of the script**.

## Deliverables

| File | What it must contain |
|---|---|
| `episodes/<slug>/script.txt` | The full voiceover, plain text. Must include the exact line `That's the mechanism.` Paragraphs are TTS breath groups (separated by a blank line). Target 35–55 s spoken (roughly 90–140 words at this pacing). |
| `episodes/<slug>/sources.json` | Every factual claim, ≥2 source URLs, and a confidence tag. Schema follows the pilot files (see `episodes/01-qr-code/sources.json`). |
| `episodes/<slug>/shots.md` | Shot table consumed by `scripts/lint_shots.py`: start phrase, camera, transition, on-screen text, SFX. Phrases must occur in the script so `timing.makeAt(words)` can resolve them. |
| `episodes/<slug>/brief.md` | Subject, pillar, special moment, angle. |

## How to write

1. Open with the object, not a title card. The first sentence is the hook; the subject will be on screen at 0.3 s.
2. Build tension, then 2–3 mechanism beats, then a turn, then the catchphrase, then a 6–10 word callback that can loop into the hook.
3. Prefer concrete numbers and named mechanisms over vague wonder. If a number cannot be sourced twice, drop it.
4. Sources must be primary or close-to-primary (inventor docs, standards, measurement studies, textbooks). Do not cite a random blog as the only backup. Wikipedia is acceptable as one of two sources only when it points at a checkable reference.
5. Record the special moment (the on-screen proof) in the brief and make sure the script leaves time for it.
6. Run `python3 scripts/lint_shots.py <slug>` once captions exist (or earlier, knowing phrase times will be validated after TTS). Fix lint failures before calling the script done.

## Lint expectations (also in docs/ACCEPTANCE.md)

- No fades as transitions.
- ≤8 words per on-screen text.
- No three pushes in a row.
- A beat every ≤3 s; first beat <1 s.
- Spoken phrases in the shot table resolve against the caption words.

## Rules

- Fact-check with **2+ independent sources per claim**. Never invent a figure.
- Do not publish research as if it were already a video. Wait for approval, then `voice` / `build-episode.sh`.
- English is the on-camera language of the channel unless a human asks otherwise.

## Fact ledger gate (round 5)
- Every spoken claim lives in `episodes/<slug>/facts.json` (`f-0001…`, status `verified|contested|unverified`, ≥2 `sources` ids from the same file, `caveat`, `checkedAt`, `spoken` = exact substrings of script.txt). Start from an old `sources.json` with `scripts/facts.py init <slug>`.
- `scripts/facts.py check <slug>` fails if a spoken fact is not verified, a spoken fact has one source and no caveat, a `spoken` span went stale, or **any number/quantity word in the script is not covered by a verified fact's span**.
- `scripts/tts.py` refuses to voice a script while `facts.py check` fails or the `script` gate is closed (`pipeline.config.json`). Re-open the source pages when you mark something verified; don't promote statuses from memory.
