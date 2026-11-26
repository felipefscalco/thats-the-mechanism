# Decision log

Dated decisions that used to live in chat or research pages. **Do not reopen a settled item** without a new, written reason. Format: date, decision, why, and what was rejected when that matters.

Related living docs: [`AGENTS.md`](../../AGENTS.md), [`STYLE_BRIEF.md`](../STYLE_BRIEF.md), [`QUEUE_AND_PUBLISH.md`](../QUEUE_AND_PUBLISH.md), [`BACKLOG.md`](../BACKLOG.md).

## 2026-11-18 — Language and market

**Decision:** English-first, aimed at high-CPM markets with heavy YouTube use. The channel need not be about Japan.

**Why:** USD-level ad rates and global reach. AI can cross the language barrier.

**Rejected:** a Japan-focused channel as the starting brief.

## ~2026-11-19 — Faceless Shorts, not on-camera reviews

**Decision:** Short faceless explainers, not a labour-heavy on-camera AI-tool review format.

**Why:** The review format did not fit a highly automated pipeline. Faceless Remotion explainers match what was already working in Claude Code + Remotion Reels, and are easier to defend under YouTube inauthentic-content rules than a generic “did you know?” template.

**Rejected:** the on-camera senior-engineer AI-tools review plan (research page of 2026-11-19).

## 2026-11-19 — Format, name, and catchphrase

**Decision:** Format A, **That's the Mechanism**. 35–55 s. Hook → tension → mechanism → turn → “That's the mechanism.” plus a short callback and an exact loop. Intended handle `@thatsthemechanism`.

**Why:** A fixed close builds the brand; the mechanism itself must be unique every time. The format demands a real explanation, which fits code-driven diagrams.

**Rejected:**

- **Almost Right** (“Almost. Here's the actual reason.”) — strong for myth-busting, risk of sounding pedantic.
- **One Number** (“That's where the number comes from.”) — easy to chase shock figures; every video would need a hard source.
- Other names: The Non-Obvious, The Hidden Reason, Show the Mechanism, The Engineer's Why (`@themechanism` was already taken).

## 2026-11-19 — Cadence (plan, not yet running)

**Decision:** Target five Shorts a week, Monday–Friday, same time (the plan used 21:00 JST / 09:00 ET), with a go/no-go around video 30 on the median, not the mean.

**Status:** The pipeline and pilots were built instead; **nothing is published**. Quality work continued through late November 2026. Do not treat the original 1 December 2026 start date as a commitment until Felipe sets a new one.

## 2026-11-19 — Monetization across three platforms

**Decision:** Grow on YouTube, TikTok, and Instagram together. Later confirmed (2026-11-25) as the main focus, with a target around **US$2,000/month** combined. Figures: [`CHANNEL.md`](CHANNEL.md).

**Rejected / out of scope for the main brand:** clipping other creators on `@thatsthemechanism`; counting on Instagram Reels bonuses; treating 35–55 s TikTok cuts as Creator Rewards inventory; building the financial plan on Shorts RPM alone.

## 2026-11-19 / 2026-11-25 — Visual style and assets

**Decision:** Editorial engineering-diagram look. Owner later picked **Look A** plus drawn backdrops (`claude-drawing-skill`) on QR and Sky, and an upgraded mechanical Look A on Elevator. Standard open/close, SFX, and an approved style-frame step before a new look is animated. **Stills must be CC0 or public domain**, verified at the source, with credits recorded. No unlicensed web images.

**Rejected:** cartoon 3D / character look that was saturating TikTok; public kinetic-text templates as the channel look; Pexels/Pixabay or other non-CC0 stock as the base; photoreal generative b-roll of real places or events as the default (allowed only as optional, labelled, and generally avoided).

## 2026-11-19 / 2026-11-25 — Voice

**Decision (current):** Kokoro `am_michael`, speed 1.08, English US. A **clone of Felipe's voice is postponed** until a professional result is ready. Prefer a local open-source tool; paying (for example ElevenLabs) is acceptable if local quality is not good enough.

**Rejected or deferred:** Qwen3-TTS as the default (tested in round 3: slow on CPU, not clearly better). F5-TTS and Fish Audio S2 Pro (non-commercial weights). Chatterbox as a long-term bet (project retired August 2026). Starting production blocked on a clone.

**Still open:** human listen of Kokoro `am_fenrir` (wider pitch range); Pocket TTS (Kyutai) as the leading local clone candidate once a consent sample exists. See [`TESTS_R5.md`](../TESTS_R5.md) and [`BACKLOG.md`](../BACKLOG.md).

## 2026-11-25 — Maximum autonomy, toggleable human gates

**Decision:** The goal is maximum autonomy. Human approval steps (angle, script, new style frames, final video; fact checks) are **temporary, toggleable gates** (`human` / `auto` / `off` in `pipeline.config.json`, via `scripts/gates.py`). They come off only when Felipe judges them unnecessary. Automated QA stays as the safety net.

**Why:** Approval should not be a permanent bottleneck, but skipping it by default is not allowed.

## 2026-11-25 — Code over prose; generic critic lessons

**Decision:** Every critic finding that should apply to future videos must be a **generic** rule, enforced as **code first**: a QA gate that blocks the render, then a Remotion component that makes the error impossible, and prose only for subjective craft. Hierarchy: [`AGENTS.md`](../../AGENTS.md#enforcement-hierarchy-code-over-prose).

## 2026-11-25 — Independent critic, pairwise ship test

**Decision:** The builder is not the judge. Ship only if a pairwise critic prefers the new render over the last approved one in at least one order and never loses in the other. A calibrated absolute score is advisory (it has not ranked versions reliably; the ship bar of 7+ has not been reached). Ties go to a second model, then to per-gate deltas.

## 2026-11-26 — LLM-agnostic roles

**Decision:** Planner, builder, fixer, critic, and later roles run through `scripts/llm.py`. The provider is set in `pipeline.config.json`, not hard-coded to Claude. Override with `LLM_<ROLE>=provider:model`.

**Why:** Felipe asked to make the pipeline generic for several LLMs, not only Claude, and later to leave enough repo context to try Claude, Gemini, and others on the Mac.

## 2026-11-26 — Topic queue and publish pack (approved)

**Decision:** Felipe approved the design, then asked that it be well documented ([`QUEUE_AND_PUBLISH.md`](../QUEUE_AND_PUBLISH.md)). Topics live in `topics.jsonl` and need `approved === true`. `pipeline.py --batch --stop-at <stage>` is resumable. A publish pack is written for review; **upload is a stub that refuses**. An `APPROVED` file that Felipe creates would be required even if upload is later implemented. Idempotent posting IDs, no double post.

**Rejected:** automatic posting (including headless “factory” uploaders).

## 2026-11-26 — Hooks: machinery on, current scripts kept

**Decision:** The hook step (3–5 candidates, code ban list, judge) stays in the pipeline for new topics. For Sky and Elevator, **keep the current hooks**. Do not apply “Where does a sunset's missing blue end up?” or “Half the weight in an elevator shaft is hanging there for no one.” without a new script approval.

**Rejected for this channel:** clickbait formulas such as “wait, don't scroll”, “hey guys”, “today I'll show you”.

## 2026-11-26 — Callout-clutter gate counts floating callouts only

**Decision:** The excess-label test counts **only free-floating callouts**, not diagram labels (for example TagLabels on a schematic). Felipe chose this after ANC flagged 4–6 diagram labels at once.

## 2026-11-26 — No per-stage time or step limits

**Decision:** After round 9, speed work may add a ready context bundle, a parallel critic, and a timing report. **Do not add a time or step cap per stage.**

**Why:** Felipe judged that a cap could cut quality mid-run. Quality first. Planner/builder slowness should be fixed with a tighter context pack, not a kill switch.

## Other standing “no”s

- Do not use MoneyPrinterTurbo-style stock footage, bundled YouTube-ripped music, unofficial Edge TTS as the primary voice, or Pexels/Pixabay as licensed stills.
- Do not buy or install Promptkura for hooks (see [`RESEARCH.md`](RESEARCH.md)).
- Do not describe a voice clone or Qwen3-TTS as shipping.
- Do not treat `IceDemo` as a shippable episode.
- Do not commit or print secrets, tokens, or `.env` files.
