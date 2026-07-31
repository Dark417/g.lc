#!/usr/bin/env bash
# PostToolUse hook: auto-format edited files. Best-effort; never blocks.
set -euo pipefail

file="${CLAUDE_TOOL_INPUT_file_path:-}"
[ -z "$file" ] && exit 0
[ -f "$file" ] || exit 0

case "$file" in
  *.py)        command -v ruff      >/dev/null && ruff format "$file"      || true ;;
  *.ts|*.tsx)  command -v prettier  >/dev/null && prettier -w "$file"      || true ;;
  *.js|*.jsx)  command -v prettier  >/dev/null && prettier -w "$file"      || true ;;
  *.go)        command -v gofmt     >/dev/null && gofmt -w "$file"         || true ;;
esac

exit 0
