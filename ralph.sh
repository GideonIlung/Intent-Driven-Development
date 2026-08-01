#!/usr/bin/env bash
#
# ralph.sh — the dumb orchestrator.
# Spawns a fresh, context-clean agent each iteration until every story in prd.json
# has passes:true, or max iterations is reached. Project-agnostic: it knows nothing
# about the project — the agent reads prd.json + AGENTS.md + ralph_prompt.md.
#
# Usage:
#   ./ralph.sh [max_iterations]                     # default 10
#   RALPH_AGENT=claude ./ralph.sh 5
#
# Each harness has its own model variable, so you can keep both set at once and
# switch harness with RALPH_AGENT alone:
#   RALPH_OPENCODE_MODEL=opencode/big-pickle
#   RALPH_CLAUDE_MODEL=sonnet
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRD_FILE="$SCRIPT_DIR/prd.json"
PROMPT_FILE="$SCRIPT_DIR/ralph_prompt.md"
PROGRESS_FILE="$SCRIPT_DIR/progress.txt"

# ---- Config (edit these) -------------------------------------------------
AGENT="${RALPH_AGENT:-opencode}"      # opencode | claude

# OpenCode: "provider/model". Confirm the exact string with `opencode models`.
OPENCODE_MODEL="${RALPH_OPENCODE_MODEL:-opencode/big-pickle}"
# Claude Code: bare alias (sonnet|opus|haiku) or a full model id.
CLAUDE_MODEL="${RALPH_CLAUDE_MODEL:-sonnet}"

MAX_ITERATIONS="${1:-10}"
VARIANT="${RALPH_VARIANT:-}"          # opencode only
# -------------------------------------------------------------------------

# One adapter per harness. Each defines MODEL + run_agent().
case "$AGENT" in
  opencode)
    MODEL="$OPENCODE_MODEL"
    command -v opencode >/dev/null \
      || { echo "✗ opencode not found. Install: npm i -g opencode-ai"; exit 1; }
    run_agent() {
      if [[ -n "$VARIANT" ]]; then
        opencode run --model "$MODEL" --variant "$VARIANT" "$1"
      else
        opencode run --model "$MODEL" "$1"
      fi
    }
    ;;
  claude)
    MODEL="$CLAUDE_MODEL"
    # Ralph must not block on prompts. acceptEdits + an allowlist in
    # .claude/settings.json is the safe default; override if you need more.
    PERMS="${RALPH_CLAUDE_PERMS:---permission-mode acceptEdits}"
    command -v claude >/dev/null \
      || { echo "✗ claude not found. Install: npm i -g @anthropic-ai/claude-code"; exit 1; }
    # shellcheck disable=SC2086  # PERMS is intentionally word-split
    run_agent() { claude -p "$1" --model "$MODEL" $PERMS; }
    ;;
  *)
    echo "✗ RALPH_AGENT must be 'opencode' or 'claude' (got: $AGENT)"; exit 1 ;;
esac

command -v jq >/dev/null || { echo "✗ jq not found. Install: apt install jq"; exit 1; }
[[ -f "$PRD_FILE"    ]] || { echo "✗ Missing $PRD_FILE (run /change-ship first)"; exit 1; }
[[ -f "$PROMPT_FILE" ]] || { echo "✗ Missing $PROMPT_FILE"; exit 1; }
git -C "$SCRIPT_DIR" rev-parse --git-dir >/dev/null 2>&1 \
  || { echo "✗ Not a git repo. Run: git init"; exit 1; }

touch "$PROGRESS_FILE"   # the prompt reads this; make sure it exists

echo "Ralph starting — agent=$AGENT, model=$MODEL, max=$MAX_ITERATIONS"

for (( i=1; i<=MAX_ITERATIONS; i++ )); do
  echo ""
  echo "=============================================="
  echo "  Ralph iteration $i / $MAX_ITERATIONS"
  echo "=============================================="

  # Fresh agent, clean context. '|| true' so one crashed iteration
  # doesn't kill the whole loop.
  run_agent "$(cat "$PROMPT_FILE")" 2>&1 | tee /dev/stderr || true

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