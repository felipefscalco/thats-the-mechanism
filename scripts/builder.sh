#!/usr/bin/env bash
# Builder role (r7, vendor-neutral): one fresh builder session through scripts/llm.py. The provider/model come from
# pipeline.config.json llm.roles.builder (override: LLM_BUILDER=provider:model, e.g. agy:claude-sonnet-5-5 or codex:gpt-5.6).
# The full preview-first loop (plan -> build -> preview -> fixer/builder -> self-critique -> ship -> judge) is scripts/build_loop.py.
# Usage: scripts/builder.sh <CompId> <slug> <task-file> [log-dir] [SUF]
set -uo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"; PY="$P/.venv-tts/bin/python"; [[ -x "$PY" ]] || PY=python3
ID="$1"; SLUG="$2"; TASK="$3"; LOG="${4:-$P/qa/$ID/builder}"; SUF="${5:-${SUF:-v2}}"
mkdir -p "$LOG"
[[ -f "$P/docs/active_rules_prompt.txt" ]] || "$PY" "$P/scripts/lessons.py" --local >/dev/null
PROMPT="$LOG/prompt_$(date +%Y%m%d-%H%M%S).txt"
"$PY" - "$P" "$ID" "$SLUG" "$SUF" "$TASK" > "$PROMPT" <<'PYEOF'
import sys; from pathlib import Path
root, i, slug, suf, task = sys.argv[1:]
t = (Path(root) / "prompts/builder.md").read_text()
for k, v in dict(ROOT=root, ID=i, SLUG=slug, SUF=suf, MAX_TRIES=4, TASK=Path(task).read_text()).items(): t = t.replace("{" + k + "}", str(v))
print(t)
PYEOF
[[ -s "$PROMPT" ]] || { echo "builder.sh: the prompt is empty ($PROMPT); not starting an agent" >&2; exit 2; }   # r10: never call a model with nothing
SUF="$SUF" "$PY" "$P/scripts/llm.py" run --role builder --prompt-file "$PROMPT" --workdir "$P" --log-dir "$LOG" \
  --scope "remotion/src/episodes/$ID.tsx,episodes/$SLUG/*.json,episodes/$SLUG/notes*.md"
