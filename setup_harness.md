

Can you run the following so that it converts the harness to function with both claude code and opencode

```
cd ~/path/to/Intent-Driven-Development
cat > setup-harnesses.sh << 'IDDEOF'
#!/usr/bin/env bash
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repo"; exit 1; }
edit() { "$@" > /tmp/idd.$$ && mv /tmp/idd.$$ "${!#}"; }

echo "1. shared assets"
mkdir -p .agents
for d in commands skills; do
  if [ -d .agents/$d ] && [ ! -L .agents/$d ]; then :
  elif [ -d .opencode/$d ] && [ ! -L .opencode/$d ]; then git mv ".opencode/$d" ".agents/$d"
  else echo "  neither .agents/$d nor .opencode/$d — fix by hand"; exit 1; fi
done
mkdir -p .claude .opencode
for h in claude opencode; do for d in commands skills; do
  l=".$h/$d"
  if [ -L "$l" ]; then :
  elif [ -e "$l" ]; then echo "  $l exists, not a symlink — remove it"; exit 1
  else ln -s "../.agents/$d" "$l"; echo "  linked $l"; fi
done; done

echo "2. CLAUDE.md"
[ -f CLAUDE.md ] || { printf '@AGENTS.md\n' > CLAUDE.md; echo "  created"; }

echo "3. command arguments"
for f in .agents/commands/*.md; do
  case "$(basename "$f" .md)" in
    baseline) h='[capability]';; change-new) h='<slug|description>';;
    change-continue) h='[slug] [artifact]';; change-ship|change-finish) h='<slug>';;
    investigate-new) h='[slug|description]';; *) h='[slug]';;
  esac
  grep -q '^argument-hint:' "$f" || { awk -v h="$h" '
    /^---[ \t]*$/ { d++; if (d==2) print "argument-hint: " h } { print }' "$f" > "$f.t" && mv "$f.t" "$f"; }
  grep -q 'ARGUMENTS' "$f" || { awk '
    /^---[ \t]*$/ && d<2 { d++; print; if (d==2) print "\n**Argument**: `$ARGUMENTS`"; next } { print }' "$f" > "$f.t" && mv "$f.t" "$f"; }
  echo "  $(basename "$f")"
done

echo "5. doc paths"
for f in CONVENTIONS.md README.md AGENTS.md; do
  [ -f "$f" ] || continue
  sed -e 's#\.opencode/skills#.agents/skills#g' -e 's#\.opencode/commands#.agents/commands#g' \
      -e 's#^- `\.opencode/` — the commands and skills\.$#- `.agents/` — the commands and skills. Symlinked into `.claude/` and `.opencode/`.#' \
      "$f" > "$f.t" && mv "$f.t" "$f"
  echo "  $f"
done

echo "done. review: git status --short && git diff"
IDDEOF
chmod +x setup-harnesses.sh && ./setup-harnesses.sh
```


# update Ralph

```
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
```
