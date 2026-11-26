#!/usr/bin/env bash
# r6 builder role: Claude Code (claude -p) owns script/facts/scene-building and fix iterations.
# Usage: scripts/builder.sh <CompId> <slug> <task-file> [log-dir]
#   The prompt = fixed project preamble + docs/active_rules_prompt.txt (from scripts/lessons.py) + the task file.
# Token: read from ~/.secrets/claude_oauth_token into the child env only. Never echoed, logged, or written.
set -uo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"
ID="$1"; SLUG="$2"; TASK="$3"; LOG="${4:-$P/qa/$ID/builder}"
mkdir -p "$LOG"
[[ -f "$P/docs/active_rules_prompt.txt" ]] || "$P/.venv-tts/bin/python" "$P/scripts/lessons.py" --local >/dev/null
TS=$(date +%Y%m%d-%H%M%S)
PROMPT="$LOG/prompt_$TS.txt"
{
  cat <<PRE
You are the BUILDER for the "That's the Mechanism" Shorts pipeline in $P (episode $SLUG, composition $ID).
You own the script, facts, Remotion scenes and fix iterations. You are NOT the judge: an independent critic (agy) decides shipping.
Read first: AGENTS.md (especially "Enforcement hierarchy: code over prose"), docs/STYLE_BRIEF.md, docs/ACCEPTANCE.md, docs/STYLE_RULES.md, docs/LESSONS.md.
Use brand primitives instead of hand placement: Lane / LabeledBox (36 px icon/label clearance), TagLabel / Pill (built-in overshoot pop),
LoopEnd (last frame locked to the frame-0 hook). Never print, cat, or log anything under ~/.secrets or any token.
Do not publish, commit, or push. Do not edit scripts/qa.py, scripts/contrast.py or other gates to make a check pass.
Run (cd remotion && npx tsc --noEmit -p .) after edits. Render + QA with:
  SUF=<suffix> MASTER=1 scripts/iterate.sh <N> $ID      (QA report: qa/$ID/<suffix>/report_it<N>.json)
An iteration passes only when EVERY check prints PASS.

PRE
  echo "=== Active style rules (docs/active_rules_prompt.txt) ==="
  cat "$P/docs/active_rules_prompt.txt"
  echo
  echo "=== Task ==="
  cat "$TASK"
} > "$PROMPT"
T0=$(date +%s)
cd "$P"
CLAUDE_CODE_OAUTH_TOKEN="$(cat "$HOME/.secrets/claude_oauth_token")" claude -p \
  --dangerously-skip-permissions --output-format json "$(cat "$PROMPT")" > "$LOG/result_$TS.json" 2> "$LOG/stderr_$TS.log"
RC=$?
echo "builder $ID rc=$RC wall_s=$(( $(date +%s) - T0 )) result=$LOG/result_$TS.json"
exit $RC
