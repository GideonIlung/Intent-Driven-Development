#!/usr/bin/env bash
set -euo pipefail
die() { echo "✗ $*" >&2; exit 1; }
DOC="${1:-}"; [ -n "$DOC" ] || die "usage: finalise.sh <lead-document>"
[ -f "$DOC" ] || die "no such file: $DOC"
git rev-parse --git-dir >/dev/null 2>&1 || die "not inside a git repo"
fm() { awk -v k="$2" '/^---[[:space:]]*$/{d++;next} d==1 && $0 ~ "^"k":"{sub("^"k":[[:space:]]*","");gsub(/^["'\''"]|["'\''"]$/,"");print;exit}' "$1"; }
TYPE="$(fm "$DOC" type)"; ID="$(fm "$DOC" id)"; TAG="$(fm "$DOC" tag)"
[ -n "$TYPE" ] && [ -n "$ID" ] && [ -n "$TAG" ] || die "front-matter needs type, id, tag"
case "$TYPE" in
  implementation) PREFIX="impl"; ROLLBACK="git revert <commit>   # undo, keep history";;
  investigation)  PREFIX="inv";  ROLLBACK="git checkout $TAG      # revisit that state (read-only)";;
  *) die "type must be implementation|investigation (got: $TYPE)";;
esac
[ "$TAG" = "$PREFIX/$ID" ] || die "tag should be '$PREFIX/$ID' (got: $TAG)"
git rev-parse -q --verify "refs/tags/$TAG" >/dev/null 2>&1 && die "tag exists: $TAG"
git add -A
git diff --cached --quiet && die "nothing staged to commit"
git commit -q -m "$PREFIX: $ID"
git tag -a "$TAG" -m "$ID"
echo "✓ committed and tagged $TAG"
echo "  roll back:  $ROLLBACK"
