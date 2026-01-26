# LeetCode Notes + Solutions — Format Guide

Use this format for all problem writeups in this repo (category files like `26U/blind75.md`, `Order Of Phoenix/linkedlist.md`, etc.).

## File structure

- Start with a clear title: `# <Topic>` (optionally add a date section).
- Keep a **Category** section (bulleted) near the top so you can jump to problems quickly.
- Put solutions under a `## Solutions (Python)` section.

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

Each entry in the category section:
- `[E/M/H]` difficulty tag
- Problem number + name as an **in-page anchor link** (`#lc-XXXX`) to the solution below
- A short description after `—`

## Per-problem template

Use an anchor so the Category section can link to the solution section:

````md
<a id="lc-0001"></a>
#### 1. [Two Sum](https://leetcode.com/problems/two-sum/) [E]
Description: One sentence summary of the task.

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
- **Description** is a one-sentence summary of the problem.
- Each approach has an **Idea** line explaining the key insight.

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
