#!/usr/bin/env bash
# fail if .claude/ or .opencode/ copies differ from .agents/
# use in CI, or: ln -s ../../scripts/check-install.sh .git/hooks/pre-commit
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
scripts/install.sh all >/dev/null
if ! git diff --quiet -- .claude .opencode; then
  echo "tool folders out of date: run scripts/install.sh all and commit" >&2
  git diff --stat -- .claude .opencode >&2
  exit 1
fi
