# LeetCode Notes + Solutions — Format Guide

Use this format for all problem writeups in this repo (category files like `blind75/blind75.md`, `Order Of Phoenix/linkedlist.md`, etc.).

## File structure

- Start with a clear title: `# <Topic>` (optionally add a date section).
- Keep a **Category** section (bulleted) near the top so you can jump to problems quickly.
- Put solutions under a `## Solutions (Python)` section.

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

## Multiple solutions (when applicable)

- Only include **materially different** approaches (e.g., `DP` vs `BFS` vs `Greedy` vs `Union-Find`), not small tweaks of the same algorithm.
- Rank approaches by **most efficient first** (time, then space). If tied, rank by clarity / typical interview choice.

## Complexity rule

- Put complexity as a **single Python comment line inside the code block**, after the implementation:
  - `# Time: O(...), Space: O(...)`

## Code rules

- Prefer LeetCode-ready code: `class Solution:` with the standard method signature.
- For design problems, include the full class (`LFUCache`, `AllOne`, etc.).
- No printing / I/O in solutions.

