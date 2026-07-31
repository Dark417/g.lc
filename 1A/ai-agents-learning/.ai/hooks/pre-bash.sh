#!/usr/bin/env bash
# PreToolUse hook: block destructive shell commands even if the model attempts them.
# Exit 2 = block; exit 0 = allow.
set -euo pipefail

cmd="${CLAUDE_TOOL_INPUT_command:-}"

case "$cmd" in
  *"rm -rf "*|*"git push --force"*|*"DROP TABLE"*|*"DROP DATABASE"*)
    echo "blocked by pre-bash hook: $cmd" >&2
    exit 2
    ;;
esac

exit 0
