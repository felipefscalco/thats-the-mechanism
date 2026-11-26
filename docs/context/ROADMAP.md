# Roadmap

Open work and explicit non-goals. Update this file when a decision lands or a round closes. Round reports remain the source of truth for what already shipped.

## Now — round 9 (in progress)

Branch `r9` (do not assume it is merged). Generic kit fixes first, then rebuilds in order **QR → ANC → Elevator → Sky**. Each episode reaches `main` only if the pairwise critic prefers it to the current approved version.

Already in the r9 kit work (see the conversation log and the r9 branch when it is available):

- Atomic `<Label>`: text and backing animate as one unit; lint against raw text over a separately animated pill; ghost-text test (flagged the four Sky v8 instants).
- Fixed **1.5 s** end-card pause before the loop, with a test.
- Label appearance within 0.5 s of the matching narrated word.
- Measured wow / impact moment (size, centering, motion) from each episode's special moment.
- Art-bbox edge gate (the kind of clip that caught Elevator v7's car).

Settled for this round: **keep current hooks**; clutter counts **floating callouts only**; **no per-stage time or step limits**.

Still to finish: the four rebuilds and ship tests; then merge. QR and ANC still carry known r8-gate issues until they are rebuilt (QR: holds, an easing miss, a near-edge label; ANC: five floating callouts around 0:31). Elevator still needs the v6b strengths (CAR/CW labels, voice-over lock at 0:19–0:26, car inside the stage) if it is attempted again.

## After round 9 — speed, without quality caps

Felipe agreed to finish the current quality pass first, then:

1. **Ready context bundle** — planner and builder receive only what they need, so the planner does not spend a long time exploring the repo (one r9 plan step took ~18 minutes vs ~1.5 minutes earlier).
2. **Parallel critic** — judge one video while the next is already building.
3. **Timing report** — wall time per stage and round, so it is obvious where time goes.

Do **not** add a time or step limit that aborts a stage mid-run.

This context pack (`docs/context/`) is the first half of “leave all Grok Bot context in the repo” so Claude, Gemini, Codex, or Cursor can continue on the Mac. Keep it current when decisions change.

## Voice

- Record a consent sample and test **Pocket TTS** (and/or CosyVoice / GPT-SoVITS on the Mac) for a professional clone.
- Human listen of Kokoro `am_fenrir`.
- ElevenLabs remains a paid fallback if local quality is not good enough.
- Re-record first lines as title hooks once a clone exists ([`BACKLOG.md`](../BACKLOG.md)).

## Channel operations (blocked on Felipe)

- Confirm and reserve **`@thatsthemechanism`** (or another chosen handle) on YouTube, Instagram, and TikTok. Do not publish the scannable QR until this is confirmed.
- Review publish packs (Sky v8 is in `publish/03-sky/`) and only then create `APPROVED` if a pack should be upload-ready. Upload code stays a refuse-stub until a later, explicit decision.
- Set a real publish start date and cadence. The November 2026 “five a week from 1 December” plan did not start; pilots are still unpublished.
- Optional later: 61–70 s TikTok cut for Creator Rewards, once thresholds are in reach.
- Weekly metrics loop (D+2 / D+7, median vs mean, pillar performance) only after something is actually posted.

## Quality backlog worth promoting (from r8 open issues)

See also [`ROUND8.md`](../ROUND8.md) and [`BACKLOG.md`](../BACKLOG.md).

- Stronger semantic label–narration sync (the advisory `vo_sync` check does not catch the wrong state on screen).
- Automatic single retry when a ship render fails on infrastructure (transient stem/QA errors).
- Longer timeout for `critic_deep` (agy has timed out).
- Mechanical foley and camera variety on schematic-heavy episodes (Elevator critic note).

## Explicit non-goals

- Auto-publish, scheduled posting, or connecting upload APIs “just in case.”
- Stock footage factories, Pexels/Pixabay stills, uncleared music, unofficial Edge TTS.
- Buying Promptkura.
- Per-stage kill switches for speed.
- Changing Sky/Elevator hooks without a new script approval.
- Treating `IceDemo` as content.
