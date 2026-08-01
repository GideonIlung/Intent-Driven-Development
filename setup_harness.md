

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