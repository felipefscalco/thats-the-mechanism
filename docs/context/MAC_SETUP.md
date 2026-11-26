# Mac setup

How to run this pipeline on Felipe's **MacBook Pro (Apple M5)** with Homebrew, and how to point roles at Claude Code, Antigravity (`agy`), Gemini, or Codex. The pipeline was first assembled on a Linux box so it would not depend on the Mac; the same repo should run locally. A short version already lives in the [README](../../README.md#running-on-a-mac).

Requirements in general: Node.js `^20.19 || ^22.13 || >=24`, Python 3.10+, FFmpeg, git, and cmake plus a C/C++ toolchain (to build whisper.cpp).

## Install

```bash
brew install node python ffmpeg cmake git
# optional but useful: jq, uv
git clone git@github.com:felipefscalco/thats-the-mechanism.git
cd thats-the-mechanism
scripts/setup.sh --fast          # venv + npm (enough to typecheck)
(cd remotion && npx tsc --noEmit -p .)
scripts/setup.sh                 # Kokoro models + whisper.cpp (longer)
```

Apple GPUs help: Remotion's Chrome-based renderer is substantially faster on Apple Silicon than on a CPU-only Linux box, and later MLX voice tools can use the Neural Engine / GPU. You do not need a discrete NVIDIA GPU for the current Kokoro + Remotion path.

If `python` on the Mac is an asdf or Homebrew shim, make sure `scripts/setup.sh` still creates `.venv-tts` and that TTS/captions use `.venv-tts/bin/python`.

## CLI logins (pick the providers you will use)

Install and log in to each CLI on the desktop; the login flow opens a browser. Nothing needs to be pasted into the repo.

| CLI | Typical command | Used for |
|---|---|---|
| Claude Code | `claude` (then `claude setup-token` if you want a token file) | planner, builder, fixer, hooks, writer, … |
| Antigravity | `agy` | default critic / `critic_deep` / tie-break / clusterer; can also build |
| Gemini CLI | `gemini` (optional) | not the same as `gemini-api` |
| Codex | `codex` | optional builder/fixer (`codex exec`) |
| Cursor Agent | `cursor-agent` | optional builder fallback |

`scripts/llm.py detect` lists what is installed. `scripts/llm.py roles` shows the resolved role → provider:model map.

**Gemini API critic** (`provider: gemini-api`) reads `GEMINI_API_KEY` from the environment only. Free tier is about 20 calls per model per day (L-22). Prefer the `agy` critic roles when that CLI is logged in.

## Claude token path

Scripts no longer hard-code a token path. Resolution order:

1. An existing `claude` login on this machine.
2. `CLAUDE_CODE_OAUTH_TOKEN` in the environment.
3. The file named by `TTM_CLAUDE_TOKEN_FILE` (default `~/.secrets/claude_oauth_token`, created with `claude setup-token`).

Example:

```bash
mkdir -p "$HOME/Library/Application Support/ttm"
export TTM_CLAUDE_TOKEN_FILE="$HOME/Library/Application Support/ttm/claude_token"
```

The token is placed in the **child** environment only. **Never print, log, or commit it.** Keep it out of the repo (`~/.secrets/` and `secrets/` are not tracked).

## Switching models and roles

Edit `pipeline.config.json` → `llm.roles`, or override one run:

```bash
LLM_BUILDER=agy:claude-sonnet-5-5   # example
LLM_CRITIC=claude:opus
LLM_FIXER=codex:gpt-5.6
.venv-tts/bin/python scripts/llm.py roles
.venv-tts/bin/python scripts/build_loop.py Sky 03-sky v9 --prev renders/Sky_v8.mp4
```

A missing CLI falls through to that role's `fallback` list. Defaults (as of rounds 7–8) use Claude Sonnet for plan/build/fix and `agy` Gemini models for critic roles. Change them freely; do not hard-code a vendor in a new script — go through `scripts/llm.py`.

## Renders are not in git

`*.mp4` is gitignored. The pairwise critic needs the **previous approved render on disk**. Before `build_loop.py --prev`:

```bash
# rebuild the approved version from its commit, or copy the MP4 onto this machine
SUF=v8 MASTER=1 scripts/iterate.sh 1 Sky
```

Scratch, QA frames, model binaries, and `queue/state/` are also ignored. Generated narration WAV files are not committed.

## Remotion studio

Once episode audio exists at `remotion/public/<slug>.wav` (from `build-episode.sh`):

```bash
(cd remotion && npm run dev)
```

## First checks on a new Mac

```bash
scripts/setup.sh --fast
(cd remotion && npx tsc --noEmit -p .)
python3 tests/test_r7_pipeline.py          # adapter dry-run, guards
.venv-tts/bin/python scripts/llm.py detect
# after full setup.sh:
scripts/pipeline.py --preflight            # CLIs, ffmpeg, logins; exit 2 if something is missing
```

If a role CLI is missing, either install it or point that role at a provider you have. Do not paste subscription tokens into the shell history in a way that could be copied into a ticket or a commit.

## Keyboard / sandbox note

This repo is meant to be driven by **any** coding agent whose instructions start at `AGENTS.md` and [`docs/context/README.md`](README.md). `CLAUDE.md` and `GEMINI.md` only point at `AGENTS.md`.
