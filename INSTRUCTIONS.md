# LeetCode Notes + Solutions — Format Guide

This `INSTRUCTIONS.md` captures how every `26U` topic writeup and the shared log behave so the repo serves as a reliable, indexed LeetCode notebook.

## Index

Track the number of questions added per week with the `常` table below. Weeks start on Monday (Jan 05 = week 1) and belong to the month where the Monday falls, even if only one day from that week is logged in the current month. Update this table every time `26U/26u-log.md` changes.

| Month | Total | W1 | W2 | W3 | W4 | W5 |
| --- | --- | --- | --- | --- | --- | --- |
| Jan | 71 | 0 | 0 | 13 | 58 | 0 |
| Feb | 21 | 21 | 0 | 0 | 0 | 0 |

## General instructions
- Treat each registered topic file (e.g., `26U/tree.md`, `26U/trie.md`) as a structured reference: keep indexes sorted, anchors aligned, and solution blocks complete with runnable code.
- When the user asks to “update” a file, refresh both the index and the corresponding solution block(s) so the new anchor exists.

## File DIR
- Work relative to `26U/`. Topic files may live elsewhere under that directory (e.g., `26U/ds-design.md`).
- Record every question addition or update in `26U/26u-log.md` once the solution block is finished.

## User Operation
- Users usually append problems inside the solutions section, then ask you to mirror those entries in the Index.
- Similar or extended problems go under their parent in the index and immediately after the parent block in the solutions area.

## Document types
Pick the right template before editing.

### A. Single-topic
Files like `26U/tree.md`, `26U/linkedlist.md`, `26U/stack.md`, `26U/dp.md`, `26U/trie.md`, `26U/ds-design.md`, `26U/bit.md`, or `26U/状态压缩 DP.md` cover a single topic. Group the index by `Easy`/`Medium`/`Hard` with the multi-line entry structure described below.

### B. Multi-category
Files such as `26U/blind75.md` bundle techniques (Arrays, Strings, Two Pointers, etc.). Group the index by category.

### C. Event
Weekly contests, interviews, or special events use their own heading (e.g., `### Weekly Contest 486`) with the four contest problems listed beneath it.

## Minor tricks
- Similar questions get one extra indentation level beneath the parent entry in the index; do not nest them inside the solution body.
- When parsing pasted problem lists (often with concatenated tags), split the tag line on known keywords (`Tree`, `Depth-First Search`, `Dynamic Programming`, etc.) and ignore any trailing `N+` suffix.

## File structure (top-down)
Every topic file follows the same macro layout:

1. Title block (`# <Topic>` plus optional date).
2. Index section (`## Index` or `## Category`) with all entries.
3. Solutions section (`## Solutions (Python)`) listing every problem referenced in the index.
4. Optional appendices (logs, notes).

## Index rules
- Each entry spans **three lines plus a blank line**:
  1. `[E/M/H] [N. Name](https://leetcode.cn/problems/slug/)` — difficulty and link to the **Chinese** LeetCode site, and ensure the matching `<a id="lc-XXXX"></a>` below anchors the detailed solution so the index hyperlink jumps straight to that block.
  2. Two spaces, then a short description (no `Description:` prefix).
  3. Two spaces, then backtick-wrapped tags (e.g., ``  `Tree` `Depth-First Search` ``).
  4. Blank line.
- Anchor every solution via `<a id="lc-XXXX"></a>` so the index link resolves.
- Similar questions are indented once below their parent entry.
- Add new entries immediately after the last entry in the same difficulty (or after the parent for nested questions).
- Tags line in the solutions must mirror the index tags.

## Solutions guidelines
- Every block should begin with:
  1. `<a id="lc-XXXX"></a>`
  2. `#### N. [Title](https://leetcode.cn/problems/slug/) [E/M/H]`
  3. Tags (e.g., `` `Tree` `BFS` ``).
  4. Description line starting with `-`.
- After the description, list approaches as `##### Approach 1: Name` followed by a short explanation sentence.
- Include the most efficient/interview-friendly approach first and add up to 1–2 materially different variants.
- Always provide runnable code (`class Solution:`) without printing or input parsing.
- End each code block with the complexity comment `# Time: ..., Space: ...`.
- Related problems go directly after their parent block, using the same four-line header format.

## Multiple-solution policy
- Limit to 2–3 approaches per problem with a short idea sentence for each.
- Include variants only when they offer a distinctly new perspective.

## Complexity rule
- Add `# Time: ..., Space: ...` inside every code block after the implementation.

## Code rules
- Import modules only when necessary (`collections`, `heapq`, `math`, etc.).
- Prefer canonical LeetCode class methods; helper functions may be nested inside the class.
- Follow the naming conventions outlined later in this document.

## Formatting encore
- Link every problem title in the solutions to the LeetCode slug (`https://leetcode.com/problems/{slug}/`), even if the index points to the Chinese site.
- Use zero-padded `<a id>` anchors to match the index exactly.
- Keep the index near the top and solutions ordered the same way.

## Pasted question list processing
When users paste metadata blocks (name, acceptance, difficulty, tags):
1. Split the concatenated tag line on known keywords (e.g., `Tree`, `DP`, `Array`, `Breadth-First Search`), drop the trailing `N+`.
2. Insert the entry into the index with the three-line format and the Chinese link.
3. Mirror those tags beneath the solution header.

## `26U/Tiktok.md` workflow
- Keep `## Category` at the top and detail sections below.
- Every new question needs an index bullet and a matching `### Title` heading with a hyphenated anchor (e.g., `### 5. 最长回文子串`).
- Mention the primary technique in the index description.
- After editing `Tiktok.md`, update `26U/26u-log.md`.

## `26U/26u-log.md` — Daily progress log
- Log one bullet per question under `#### Mon DD`.
- Format: `- [E/M/H] [N. Title](/26U/<file>.md#lc-XXXX)`.
- Entries must be chronological and reference fully-documented solutions.
- Update the `常` table above whenever you add a log entry.

## Git push instructions
When asked to push, stage all modified files, write a concise commit message describing the scope, and push to `main`.

## Naming conventions (succinct)
- `l`, `r` = left and right pointers
- `i`, `j`, `k` = loop indices
- `n`, `m` = lengths
- `cur`, `nxt`, `prv` = current/next/previous
- `cnt` = count, `res` = result, `ans` = answer
- `idx` = index, `val` = value
- `lo`, `hi` = low/high bounds
- `st` = stack, `q` = queue, `d` = dict/map
- `t` = target
- `p`, `f` = fast/slow pointers
- `pre`, `suf` = prefix/suffix
- `dp` = dynamic programming table
- `g` = graph (adjacency list)
- `vis` = visited set
- `h` = heap
