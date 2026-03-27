---
name: push-git
description: Stage all changes, create a concise commit, and push to the target branch. Default to `main` unless the user specifies otherwise.
---

# push-git

1. Review `git status` to understand the current workspace state.
2. Stage all intended changes.
3. Create a concise commit message if the user did not provide one.
4. Push to `main` unless the user specifies another branch or remote behavior.
5. Summarize the commit id, branch, and push result.
