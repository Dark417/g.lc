# LeetCode Notes + Solutions — Format Guide

Use this format for all problem writeups in this repo (category files like `26U/blind75.md`, `Order Of Phoenix/linkedlist.md`, etc.).

## File structure

- Start with a clear title: `# <Topic>` (optionally add a date section).
- Keep a **Category** section (bulleted) near the top so you can jump to problems quickly.
- Put solutions under a `## Solutions (Python)` section.

## Topic-specific format (topicname.md)

`26U/tree.md` exhibits the canonical format for `topicname.md` files. Each registered topic file must match this structure:

- **Title block**: `# <Topic>` plus any optional date heading.
- **Category index**: Start with `## Category` (people often label it `## Index` instead) followed by `### <Difficulty>`, and list entries as multi-line groups. The entry line (line 1) must end with a single backslash (`\`) to force the description onto the next line, the description line (line 2) must also end with a single backslash, and the tag line (line 3) lists backtick-wrapped tags. Leave a blank line between entries; never put the description or tags inline with the entry line.
- **Solutions**: Keep `## Solutions (Python)` with per-problem anchors, headers, tag lines, descriptions, and runnable `class Solution` blocks per the broader rules.
- **Index tags**: Every index entry must include a tag line similar to those in `tree.md`; missing tags are a format violation.
- **Update requests**: If the user asks to “update `**.md`” for a file in the registered list, refresh the entire file to align with this format—including all index entries and solution layout—even if only one question changed.

### Registered topic files

- `26U/tree.md`
- `26U/linkedlist.md`
- `26U/stack.md`
- `26U/dp.md`

Extend this list as other topic files adopt the same tree-style structure.

## Document types

### A. Multi-category (e.g., `26U/blind75.md`)

For files covering multiple topics. Group the index by category:

```md
## Category

### Arrays & Hashing
- [E] [1. Two Sum](#lc-0001) — Find two indices whose values add up to a target.
- [M] [49. Group Anagrams](#lc-0049) — Group words that are anagrams of each other.

### Two Pointers
- [E] [125. Valid Palindrome](#lc-0125) — Check if a string is a palindrome.
- [M] [15. 3Sum](#lc-0015) — Find unique triplets that sum to zero.
```

### B. Single-topic (e.g., `linkedlist.md`, `hashmap.md`)

For files covering one specific type. Group the index by difficulty:

```md
## Category

### Easy
- [E] [1. Two Sum](#lc-0001) — Find two indices whose values add up to a target.
- [E] [217. Contains Duplicate](#lc-0217) — Determine if any value appears at least twice.

### Medium
- [M] [49. Group Anagrams](#lc-0049) — Group words that are anagrams of each other.

### Hard
- [H] [76. Minimum Window Substring](#lc-0076) — Smallest window covering all characters of a pattern.
```

### C. Weekly contest

```md
## Category

### Weekly Contest 486
- [E] [Q1. Problem Name](#lc-3840) — Brief description.
- [M] [Q2. Problem Name](#lc-3841) — Brief description.
- [M] [Q3. Problem Name](#lc-3842) — Brief description.
- [H] [Q4. Problem Name](#lc-3843) — Brief description.
```

## Index entry format

Each entry in the category section now uses a multi-line format:
- `[E/M/H]` difficulty tag + problem number + name as an **in-page anchor link** (`#lc-XXXX`), with **no trailing description** on this line.
- (indented) A short description of the problem on the next line.
- (indented) Backtick-wrapped tags on the third line.
- Follow each entry with a blank line so the next question starts cleanly.

## Adding questions always includes solutions

When adding **any** question (standalone or similar/extended), always include at least one solution. Follow the solution priority:
1. Most efficient / most commonly expected approach
2. 1–2 alternative approaches if materially different (e.g., binary search, two pointers, greedy also works)
3. Usually 1–3 total solutions is optimal

Never add a question header without a code solution unless explicitly told to skip.

## Per-problem template

Use an anchor so the Category section can link to the solution section:

````md
<a id="lc-0001"></a>
#### 1. [Two Sum](https://leetcode.com/problems/two-sum/) [E]
`Array` `Hash Table`
- Find two indices whose values add up to a target using a hash map.

##### Approach 1: Hash map
Idea: One sentence about the key invariant / data structure.

```python
class Solution:
    def twoSum(self, nums, target):
        ...
# Time: O(n), Space: O(n)
```
````

- The **anchor** `<a id="lc-XXXX"></a>` (4-digit padded) lets the index link to the solution.
- The **problem name** hyperlinks to the actual LeetCode problem URL.
- **Tags** should be on the second line after the header, wrapped in backticks, to mirror the category index.
- **Short description** immediately follows on the third line as a hyphen bullet (drop the `Description:` prefix).
- Leave a blank line between the description and the first approach so the tags/description stand apart from the code.

Each question detail must follow the ordered pattern: heading, tag line, `- short desc`, blank line, and then the solution approaches so readers can consistently glance at the synopsis before the code.

## Multiple solutions (when applicable)

- Only include **materially different** approaches (e.g., `DP` vs `BFS` vs `Greedy` vs `Union-Find`), not small tweaks.
- Rank approaches by **most efficient first** (time, then space). If tied, rank by clarity / typical interview choice.
- Usually 2–3 total solutions is optimal.

## Solution priority

1. **Primary solution** (required): Most efficient, most commonly asked in interviews.
2. **Variant solutions** (1–2 if applicable): Materially different approaches only, ordered by intuitiveness.

## Complexity rule

- Put complexity as a **single Python comment line inside the code block**, after the implementation:
  - `# Time: O(...), Space: O(...)`

## Code rules

- Prefer LeetCode-ready code: `class Solution:` with the standard method signature.
- For design problems, include the full class (`LFUCache`, `AllOne`, etc.).
- No printing / I/O in solutions.
- No imports unless necessary (`collections`, `heapq`, `math` OK).
- One-liners OK if readable.
- Use walrus operator `:=` when cleaner.
- Prefer `//` over `int()` for integer division.
- I prefer '灵茶山艾府' answers. For a question, if you searched his solutions, present his solutions first. If official solutions have different approaches, add them. Also follow his concise naming, style, and formatting.

## Naming conventions (succinct)

- `l`, `r` = left, right pointers
- `i`, `j`, `k` = loop indices
- `n`, `m` = lengths
- `cur`, `nxt`, `prv` = current, next, previous
- `cnt` = count, `res` = result, `ans` = answer
- `idx` = index, `val` = value
- `lo`, `hi` = low, high bounds
- `st` = stack, `q` = queue, `d` = dict/map
- `t` = target
- `p`, `f` = fast/slow pointers
- `pre`, `suf` = prefix, suffix
- `dp` = dynamic programming table
- `g` = graph (adjacency list)
- `vis` = visited set
- `h` = heap

## Formatting rules

- Anchor format: `<a id="lc-XXXX"></a>` (4-digit padded)
- LeetCode URL: `https://leetcode.com/problems/{slug}/`
- Difficulty tags: `[E]`, `[M]`, `[H]`
- Always link problem title to LeetCode page in solution section
- Always include in-page anchor link in category index
- Derive problem slugs from problem names (lowercase, hyphenated)

## Similar / extended questions

When the user says **"add ###.Q to XXX question"** or **"extend ###.Q to XXX question"**, the new question is a similar/related problem that belongs under an existing parent question.

### In the Category index
Add a nested bullet (indented once) under the parent entry:

```md
- [H] [124. Binary Tree Maximum Path Sum](#lc-0124) — Find the maximum path sum in a binary tree.
  `Tree` `Depth-First Search` `Dynamic Programming` `Binary Tree`
  - [H] [2538. Difference Between Maximum and Minimum Price Sum](#lc-2538) — Max difference of subtree price sums.
    `Tree` `Depth-First Search` `Dynamic Programming`
```

### In the Solutions section
Insert the new question **immediately after** the parent question's block, with **no indentation** — use the same formatting as any other problem:

````md
<a id="lc-0124"></a>
#### 124. [Binary Tree Maximum Path Sum](...) [H]
`Tree` `Depth-First Search` `Dynamic Programming`
Description: ...

...parent solution...

<a id="lc-2538"></a>
#### 2538. [Difference Between Maximum and Minimum Price Sum](...) [H]
`Tree` `Depth-First Search` `Dynamic Programming`
Description: ...

```python
...
```
````

## Pasted question list processing

When the user pastes a list of LeetCode questions in this format:

```
297. Serialize and Deserialize Binary Tree
60.0%
困难

TreeDepth-First SearchBreadth-First SearchDesign2+
```

Each block has: problem name, acceptance rate, difficulty (简单/中等/困难), blank line, then **tags** on the last line (concatenated tag names like `TreeDepth-First SearchDesign2+`).

Processing rules:
1. **Extract tags** from the last line by splitting on known tag boundaries (e.g., `Tree`, `Depth-First Search`, `Dynamic Programming`, `Binary Tree`, `Array`, `Hash Table`, `Breadth-First Search`, `Design`, `Graph`, `Topological Sort`, `Bit Manipulation`, etc.). Trailing `N+` (e.g., `2+`) means N additional tags are omitted — ignore the suffix.
2. **Category index** — add tags on the **next line** of each question entry, indented with two spaces, as backtick-wrapped items:
   ```md
   - [H] [297. Serialize and Deserialize Binary Tree](#lc-0297) — Design an algorithm to serialize and deserialize a binary tree.
     `Tree` `Depth-First Search` `Breadth-First Search` `Design`
   ```
3. **Solution section** — also add the tags line directly below the problem header:
   ```md
   <a id="lc-0297"></a>
   #### 297. [Serialize and Deserialize Binary Tree](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/) [H]
   `Tree` `Depth-First Search` `Breadth-First Search` `Design`
   Description: ...
   ```

## `26U/Tiktok.md` — TikTok-specific workflow

`26U/Tiktok.md` is another multi-category tracker. Keep the `## Category` section near the top and the detailed question sections below. Every new question you add needs a matching index entry so readers can jump straight to it:

- Use the template `- [E/M/H] [N. Title](#anchor) — short description of the key idea` for each index bullet (for example: `- [M] [5. 最长回文子串](#5-最长回文子串) — Expand around centers to track the longest palindromic substring.`).
- Pick the topic heading (Strings, Arrays & Hashing, Backtracking, etc.) that best reflects the primary technique before inserting the bullet so the index stays grouped sensibly.
- Summarize the technique in the short description (DFS/backtracking, two pointers, digit math, etc.) so the index is still a useful skim sheet.
- Make sure the anchor matches the `### N. Title` heading (lowercase, hyphenated, roman numerals lowercased) so the link lands on the right block.
- After updating `Tiktok.md`, follow the log rules above to add the same questions to `26U/26u-log.md` so every addition is recorded.

## `26U/26u-log.md` — Daily progress log

This file tracks every question added or updated, grouped by day in reverse-chronological order.

### When to add an entry
1. **Automatically** — whenever a question is added/updated in any topic `.md` file, also append a record here.
2. **Manually** — when the user says "add ###.SomeQuestion" directly to the log.

### Format

```md
#### Jan 26
- [H] [2538. Difference Between Maximum and Minimum Price Sum](/26U/tree.md#lc-2538)
- [M] [236. Lowest Common Ancestor of a Binary Tree](/26U/tree.md#lc-0236)

#### Jan 25
- ...
```

### Rules
- Group by day heading: `#### Mon DD` (e.g., `#### Jan 26`). Latest day on top.
- Within each day, entries are **chronological** (earliest first).
- Each entry is a single bullet line that links to the question's solution; do not log tags or descriptions here.
- Every entry **must** correspond to a solution that exists in a topic `.md` file — never log a question without having its detail elsewhere.


## Git push instructions

When asked to “push” or “commit,” stage all modified files, craft a concise commit message describing what changed, and push to the `main` branch.
