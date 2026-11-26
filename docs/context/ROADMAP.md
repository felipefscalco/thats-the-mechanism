# Roadmap

Open work and explicit non-goals. Update this file when a decision lands or a round closes. Round reports remain the source of truth for what already shipped.

## Now — pipeline on main; Felipe tests on the Mac

Round 9 landed on `main` (`40c17bb`). **QR v7 shipped.** ANC, Elevator, and Sky were deferred by Felipe's mid-round scope change (2026-11-26); ready task files are in `qa/tasks/r9_*.md`. Full report: [`ROUND9.md`](../ROUND9.md).

**Next:** Felipe will test the pipeline via **orca on his Mac**, from `main`. See [`MAC_SETUP.md`](MAC_SETUP.md).

### Open decisions

- When to run the deferred ANC, Elevator, and Sky r9 loops.
- When (or whether) to run the deferred **Opus 5.5 A/B** (below).

### Quality follow-ups from round 9

- Preview passed twice, then the full ship render failed cadence, entrances, and label gates. The still-based preview is too loose; consider running label checks on a cheap low-res preview render, or tighten preview cadence.
- `labels_persist` conflicts with planned label swaps in one shot (BYTES GO MISSING → MISSING BYTES: REBUILT). `shots.md` needs per-label windows, or `@phrase` end times.
- No gate yet for caption line count or caption-to-deck clearance (the critic's top QR v7 blocker at 0:13).
- The hero gate measures size and motion, not novelty (the QR hero reused the hook card).

## Speed work, without quality caps

Planned after the quality pass (and useful to try on the Mac):

1. **Ready context bundle** — planner and builder receive only what they need, so the planner does not spend a long time exploring the repo (one r9 plan step took ~18 minutes vs ~1.5 minutes earlier).
2. **Parallel critic** — judge one video while the next is already building.
3. **Timing report** — wall time per stage and round, so it is obvious where time goes.

Do **not** add a time or step limit that aborts a stage mid-run.

**Deferred (Felipe):** a speed A/B of Claude Opus 5.5 at Medium effort for planner, builder, and `critic_tiebreak`, keeping Haiku/Sonnet for cheap, well-scoped roles; drop “think hard/carefully” phrasing; state the finished output and the stop condition up front; attach stills instead of transcribing values; name the styles to avoid. Validate on one episode (wall time, cost, verdict) before adopting it.

This context pack (`docs/context/`) is on `main` so Claude, Gemini, Codex, Cursor, or orca can continue from the same tree. Keep it current when decisions change.

## Voice

- Record a consent sample and test **Pocket TTS** (and/or CosyVoice / GPT-SoVITS on the Mac) for a professional clone.
- Human listen of Kokoro `am_fenrir`.
- ElevenLabs remains a paid fallback if local quality is not good enough.
- Re-record first lines as title hooks once a clone exists ([`BACKLOG.md`](../BACKLOG.md)).

## Channel operations (blocked on Felipe)

- Confirm and reserve **`@thatsthemechanism`** (or another chosen handle) on YouTube, Instagram, and TikTok. Do not publish the scannable QR until this is confirmed.
- Review publish packs (`publish/01-qr-code/` for QR v7, `publish/03-sky/` for Sky v8) and only then create `APPROVED` if a pack should be upload-ready. Upload code stays a refuse-stub until a later, explicit decision.
- Set a real publish start date and cadence. The November 2026 “five a week from 1 December” plan did not start; pilots are still unpublished.
- Optional later: 61–70 s TikTok cut for Creator Rewards, once thresholds are in reach.
- Weekly metrics loop (D+2 / D+7, median vs mean, pillar performance) only after something is actually posted.

## Quality backlog (older)

See also [`ROUND8.md`](../ROUND8.md), [`ROUND9.md`](../ROUND9.md), and [`BACKLOG.md`](../BACKLOG.md).

- Stronger semantic label–narration sync (the advisory `vo_sync` check still does not catch the wrong state on screen). Round 9 added hard `label_sync`, but QR v7 still failed it.
- Mechanical foley and camera variety on schematic-heavy episodes (Elevator critic note).

Round 9 already shipped a single infrastructure retry for ship render/QA crashes, and a 1800 s `critic_deep` timeout.

## Explicit non-goals

- Auto-publish, scheduled posting, or connecting upload APIs “just in case.”
- Stock footage factories, Pexels/Pixabay stills, uncleared music, unofficial Edge TTS.
- Buying Promptkura.
- Per-stage kill switches for speed.
- Changing Sky/Elevator hooks without a new script approval.
- Treating `IceDemo` as content.
