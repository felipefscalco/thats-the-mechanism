# Project context — That's the Mechanism

**Resumo (PT-BR):** este pacote reúne o que antes vivia só nas conversas do assistente: o conceito do canal, as decisões (com data e motivo, inclusive o que foi recusado), como o Felipe quer que o trabalho seja feito, o histórico das rodadas 1–9, a pesquisa de referências e o que ainda está aberto. Os docs canônicos de estilo, QA, fila e publicação continuam em `docs/` e no `AGENTS.md` — aqui só há o contexto que faltava. Um LLM novo deve seguir a ordem de leitura abaixo, não republicar nada, e tratar gates humanos como obrigatórios até o Felipe desligá-los. Nada neste repositório publica sozinho.

This folder is the **onboarding pack** for any LLM or coding agent (Claude Code, Gemini / Antigravity, Codex, Cursor, or anything else) continuing the work on Felipe's Mac or elsewhere. It records decisions and history that used to live only in chat. It does **not** replace the canonical runbooks.

## How to onboard (read order)

1. This file, then [`CHANNEL.md`](CHANNEL.md) — what the channel is, who it is for, and the monetization goal.
2. [`../STYLE_BRIEF.md`](../STYLE_BRIEF.md) and the summary in [`../../AGENTS.md`](../../AGENTS.md) — look, motion, sound, structure, hard rules.
3. [`WORKING_AGREEMENTS.md`](WORKING_AGREEMENTS.md) — how to work: code over prose, approval gates, no auto-publish, secrets, commits.
4. [`DECISIONS.md`](DECISIONS.md) — dated decisions and rejected options. Do not reopen a settled decision without a new reason.
5. The stage skill you are about to run, under `skills/<name>/SKILL.md`.
6. [`../LESSONS.md`](../LESSONS.md), [`../STYLE_RULES.md`](../STYLE_RULES.md), and [`../active_rules_prompt.txt`](../active_rules_prompt.txt) before writing a script or touching Remotion.
7. [`HISTORY.md`](HISTORY.md) if you need scores, ship verdicts, or why a version is on `main`.
8. [`RESEARCH.md`](RESEARCH.md) before adopting an outside tool or skill.
9. [`ROADMAP.md`](ROADMAP.md) for open work. [`MAC_SETUP.md`](MAC_SETUP.md) if you are running on a Mac.

## What is already documented elsewhere (link, do not copy)

| Topic | Where |
|---|---|
| Canonical agent instructions, roles, hierarchy | [`AGENTS.md`](../../AGENTS.md) (`CLAUDE.md` and `GEMINI.md` only point there) |
| Style, palette, motion, structure | [`STYLE_BRIEF.md`](../STYLE_BRIEF.md), [`STYLE_RULES.md`](../STYLE_RULES.md) |
| Acceptance / QA checklist | [`ACCEPTANCE.md`](../ACCEPTANCE.md), [`../../TESTS.md`](../../TESTS.md) |
| Critic lessons and backlog | [`LESSONS.md`](../LESSONS.md), [`BACKLOG.md`](../BACKLOG.md) |
| Topic queue and publish pack | [`QUEUE_AND_PUBLISH.md`](../QUEUE_AND_PUBLISH.md) |
| Round reports and timings | [`ROUND6.md`](../ROUND6.md), [`ROUND7.md`](../ROUND7.md), [`ROUND8.md`](../ROUND8.md), [`ITERATIONS.md`](../ITERATIONS.md), [`METRICS.md`](../METRICS.md) |
| Pilot titles, descriptions, credits | [`../../metadata.md`](../../metadata.md) |
| Licences | [`../../LICENSES.md`](../../LICENSES.md), [`ASSET_LICENSES_R5.csv`](../ASSET_LICENSES_R5.csv) |

## Standing constraints (every session)

- Nothing is published, scheduled, or uploaded without Felipe's explicit approval of that specific video.
- The pipeline is **LLM-agnostic**: roles are set in `pipeline.config.json` (override with `LLM_<ROLE>=provider:model`).
- Lessons become **code first** (gate, then component, then prose).
- Prefer a ready context bundle over wandering the repo; do not invent facts or numbers.
