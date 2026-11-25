# Lessons learned (review log)

Every reviewer (human or any LLM/agent) MUST read this file before working on an episode or the brand kit, and MUST append to it after each review.

## How to log
One entry per finding. Newest at the bottom. Format:

```
### L-<number> · <YYYY-MM-DD> · <episode or "kit"> · <severity: blocker|major|minor>
- Problem: what was wrong (observable, e.g. "label clipped at right edge at 0:12").
- Root cause: why it happened (code/kit/script decision).
- Fix: what changed (file + short description), or "open".
- Prevention: the rule, check, or kit change that stops it repeating. Prefer an automated check in scripts/qa.py or docs/ACCEPTANCE.md over a prose rule.
- Status: fixed | open | wontfix (reason)
```

## Rules
- Before reviewing, scan Prevention lines; check the episode against each one.
- A finding that already has an entry is a regression: reopen that entry, mark severity at least major, and add an automated check if there was none.
- When a Prevention becomes an automated check or kit default, write where (e.g. "qa.py: motion_gap").
- Suggestions/ideas that are not bugs go to docs/BACKLOG.md, not here.

## Entries (seeded from rounds 1-2, see docs/ITERATIONS.md)
### L-1 · 2026-11-25 · kit · major
- Problem: camera punch pushed art into captions/brand bar.
- Root cause: labels lived on the camera layer.
- Fix: verdict labels moved to a camera-locked layer.
- Prevention: overlays and labels never on the camera layer; QA safe-zone check.
- Status: fixed
### L-2 · 2026-11-25 · kit · major
- Problem: 2.5-8.4 s stretches with no motion.
- Root cause: shots planned per sentence, not per beat.
- Fix: added beats; motion gate.
- Prevention: motion never stalls > 2 s (qa.py motion check); beat every <= 3 s in the shot table.
- Status: fixed
### L-3 · 2026-11-25 · Elevator · minor
- Problem: elements in the platform right-hand button column.
- Root cause: layout ignored platform UI.
- Fix: bars re-centred.
- Prevention: respect safe zones in docs/STYLE_BRIEF.md.
- Status: fixed
### L-4 · 2026-11-25 · kit · major
- Problem: loop broke (captions/chapter label lingering in last frame; template loop bug).
- Root cause: outro did not reset overlays.
- Fix: shared loop code fixed; overlays cleared before whip.
- Prevention: QA first/last frame PSNR >= 45 dB.
- Status: fixed
