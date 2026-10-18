#!/usr/bin/env bash
# usage: scripts/ralph.sh <slug>
# env: IDD_AGENT=claude|opencode  MAX_TRIES=3  CLAUDE_FLAGS  OPENCODE_FLAGS
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
slug="$1"; agent="${IDD_AGENT:-claude}"; max="${MAX_TRIES:-3}"
dir="work/changes/$slug"; log=".idd/timing.log"; mkdir -p .idd

run_agent() {  # $1 = packet file
  case "$agent" in
    claude)   claude -p ${CLAUDE_FLAGS:---permission-mode acceptEdits} < "$1" ;;
    opencode) opencode run ${OPENCODE_FLAGS:-} "$(cat "$1")" ;;
    *) echo "unknown IDD_AGENT=$agent" >&2; exit 2 ;;
  esac
}

while story="$(scripts/idd next-story "$slug")" && [ -n "$story" ]; do
  for try in $(seq 1 "$max"); do
    t0=$(date +%s)
    packet="$(scripts/idd packet "$slug" "$story" --try "$try")"  # prints packet path
    run_agent "$packet" || true
    if grep -q '^SPEC-QUESTION:' "$dir/progress.md" 2>/dev/null; then
      echo "spec question: see $dir/progress.md"; exit 3
    fi
    if scripts/idd check "$slug" "$story"; then  # fence + gate + conform; trimmed error → .idd/
      git add -A && git commit -qm "$slug: $story [$(scripts/idd story-tags "$slug" "$story")]"
      scripts/idd mark-done "$slug" "$story"
      echo "$slug,$story,$try,pass,$(( $(date +%s) - t0 ))" >> "$log"
      continue 2
    fi
    echo "$slug,$story,$try,fail,$(( $(date +%s) - t0 ))" >> "$log"
    git checkout -q -- . ':(exclude)work/**'   # undo code, keep progress notes
    git clean -qfd -e work/
  done
  echo "$story failed $max tries: escalate"; exit 4
done
echo "all stories done"
