#!/usr/bin/env bash
#
# ralph.sh — the dumb orchestrator.
# Spawns a fresh, context-clean OpenCode agent each iteration until every story in
# prd.json has passes:true, or max iterations is reached. Project-agnostic: it knows
# nothing about the project — the agent reads prd.json + AGENTS.md + ralph_prompt.md.
#
# Usage:
#   ./ralph.sh [max_iterations]                     # default 10
#   RALPH_MODEL=anthropic/claude-sonnet-4-6 ./ralph.sh 5
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRD_FILE="$SCRIPT_DIR/prd.json"
PROMPT_FILE="$SCRIPT_DIR/ralph_prompt.md"
PROGRESS_FILE="$SCRIPT_DIR/progress.txt"

# ---- Config (edit these) -------------------------------------------------
# Model string is "provider/model". Run `opencode models` to list exact names.
MODEL="${RALPH_MODEL:-openai/gpt-5.6-sol}"
MAX_ITERATIONS="${1:-10}"
VARIANT="${RALPH_VARIANT:-}"
# -------------------------------------------------------------------------

command -v opencode >/dev/null || { echo "✗ opencode not found. Install: npm i -g opencode-ai"; exit 1; }
command -v jq       >/dev/null || { echo "✗ jq not found. Install: brew install jq"; exit 1; }
[[ -f "$PRD_FILE"    ]] || { echo "✗ Missing $PRD_FILE (run /change-ship first)"; exit 1; }
[[ -f "$PROMPT_FILE" ]] || { echo "✗ Missing $PROMPT_FILE"; exit 1; }
git -C "$SCRIPT_DIR" rev-parse --git-dir >/dev/null 2>&1 \
  || { echo "✗ Not a git repo. Run: git init"; exit 1; }

touch "$PROGRESS_FILE"   # the prompt reads this; make sure it exists

echo "Ralph starting — model=$MODEL, max=$MAX_ITERATIONS"

for (( i=1; i<=MAX_ITERATIONS; i++ )); do
  echo ""
  echo "=============================================="
  echo "  Ralph iteration $i / $MAX_ITERATIONS"
  echo "=============================================="

  # Fresh agent, clean context. OpenCode 'run' takes the prompt as a POSITIONAL
  # argument. '|| true' so one crashed iteration doesn't kill the whole loop.
  if [[ -n "$VARIANT" ]]; then
    opencode run --model "$MODEL" --variant "$VARIANT" "$(cat "$PROMPT_FILE")" 2>&1 | tee /dev/stderr || true
  else
    opencode run --model "$MODEL" "$(cat "$PROMPT_FILE")" 2>&1 | tee /dev/stderr || true
  fi

  # Stop condition = ground truth in prd.json, NOT what the model says.
  REMAINING="$(jq -c '.userStories[] | select(.passes == false)' "$PRD_FILE" 2>/dev/null || echo "")"
  if [[ -z "$REMAINING" ]]; then
    echo ""
    echo "✅ All stories pass. Ralph finished at iteration $i."
    echo "   Next: /change-finish <slug>"
    exit 0
  fi

  sleep 2
done

echo ""
echo "⚠️  Hit max iterations ($MAX_ITERATIONS). Stories still failing:"
jq -r '.userStories[] | select(.passes == false) | "  - \(.id): \(.title)"' "$PRD_FILE"
echo "   Durable specs/ untouched — do NOT run /change-finish on an incomplete build."
exit 1