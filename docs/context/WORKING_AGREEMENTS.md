# Working agreements

How Felipe wants work done in this repository. Canonical command and role detail stays in [`AGENTS.md`](../../AGENTS.md). This file captures the agreements that used to live only in chat.

## Goal

A highly automated content pipeline with as much autonomy as is safe. Human approval is a **toggleable temporary gate**, not a forever bottleneck, and **not optional today**. Automated QA is the safety net. The owner reviews; the builder does not ship its own work.

## Code over prose

Every lesson and critic rule must be **generic** (it applies to future videos, not only the one under review) and enforced in this order:

1. **Gate** — a check that blocks the render (usually `scripts/qa.py` or a sibling).
2. **Component** — a Remotion primitive that makes the error impossible.
3. **Prose** — only for subjective craft, in `docs/STYLE_RULES.md`.

A prose rule that becomes measurable must be promoted to a gate. Do not “fix it in the prompt” when a test or a component would hold. New critic `general_rules` must declare `gate`, `component`, or `prose`. `scripts/lessons.py` merges them into the style rules and `docs/active_rules_prompt.txt`.

After a review, append findings to [`LESSONS.md`](../LESSONS.md) and non-bug ideas to [`BACKLOG.md`](../BACKLOG.md). A repeated finding is a regression: reopen it and add an automated check. Commit the log with the fix.

## Approval and publishing

- **Do not publish, schedule, or upload** a video, description, or comment. Stop at a reviewed MP4, metadata, and (after round 8) a publish pack.
- Today's human gates: episode **angle**, finished **script** (with sources), **style frames** for a new look, and the **final video**. Record decisions with `scripts/gates.py approve …`. Env overrides (`GATE_MODE_X=auto`) only when asked; they are logged.
- A publish pack is for review. Upload needs a Felipe-created `APPROVED` file (and the current stub refuses anyway). Details: [`QUEUE_AND_PUBLISH.md`](../QUEUE_AND_PUBLISH.md).
- Fact-check every factual claim with **at least two independent sources** in `episodes/<slug>/sources.json`. If it cannot be sourced, cut it or flag it — never invent a number. TTS refuses until `scripts/facts.py check` passes.
- Prefer editing the shared brand kit over forking it in an episode file.

## Quality first; speed later

Do not add per-stage time or step limits. After the current quality pass, planned speed work is a **ready context bundle** (planner and builder get only what they need), a **critic that runs in parallel** with the next build, and a **timing report** per stage and round. Until that bundle exists, still prefer not to wander the whole repository when a role only needs the frozen plan and the failing checks.

## LLM roles

Roles are vendor-neutral (`scripts/llm.py` + `pipeline.config.json`). Planner, builder, fixer, and critic never share a conversation. The builder receives the frozen `VIDEO.md` and the failing checks, not a fishing expedition. Scope is enforced in code; the fixer's diff must be value-only (`scripts/fixer_guard.py`). See [`AGENTS.md`](../../AGENTS.md#llm-roles-and-adapters).

## Security

- **Never print, log, or commit secrets, tokens, or `.env` files.** That includes `GH_TOKEN`, `GEMINI_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`, and the contents of `TTM_CLAUDE_TOKEN_FILE`.
- API keys are read from the environment (or a token file into the **child** process only). Never put a key in a URL, a prompt dump, a metric log, or a credit ledger.
- `~/.secrets/` and `secrets/` are outside git (see `.gitignore`: `.env`, `*.pem`, `*.key`, `credentials.json`, `secrets/`). Do not copy those files into the repo.
- Credit URLs are sanitised (`scripts/credits.py`): no userinfo, no query tokens, no local paths.
- **Run a secret scan before every push** (search the diff and the new tree for tokens, private keys, and `.env` files).
- Shared-box hygiene: write scratch files inside the project folder, never generic `/tmp` names (L-17).

## Git and reviewability

- Keep changes reviewable: one episode or one kit fix per change set when you can.
- After animation edits, run `(cd remotion && npx tsc --noEmit -p .)` before rendering.
- Do not edit `remotion/src` while a QA batch is running (L-24).
- Do not commit rendered MP4s, model binaries, or third-party clones (see `.gitignore`). Renders stay on disk; the pairwise critic needs the previous approved MP4 locally.
- Commit messages in this repo are short, imperative English, often with a scope prefix (`Docs:`, `Gates:`, `Round 8 results:`, `Pipeline r7:`). Explain the outcome, not the essay.
- If you add a tool or sound, document the licence.
- Do not describe unshipped work (voice clone, Qwen3-TTS) as if it were in the tree.

## Communication with Felipe

Working conversation is PT-BR; **repository docs and on-screen text are English**. Ask before applying a hook or script change that needs a new approval. Do not take “go ahead on the pipeline” as permission to publish.
