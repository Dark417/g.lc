# LeetCode Weekend Contests

## Weekly Contest 486

- [E] [Q1. Minimum Prefix Removal to Make Array Strictly Increasing](#wc486-q1)
- [M] [Q2. Rotate Non Negative Elements](#wc486-q2)
- [H] [Q4. Find Nth Smallest Integer With K One Bits](#wc486-q4)

---

## Solutions (Python)

<a id="wc486-q1"></a>
### Q1. [Minimum Prefix Removal to Make Array Strictly Increasing](https://leetcode.com/problems/minimum-prefix-removal-to-make-array-strictly-increasing/) [E]

Description: Find minimum prefix length to remove so remaining array is strictly increasing.

Idea: Scan from right; find first violation where `nums[i] >= nums[i+1]`.

```python
class Solution:
    def minimumPrefixLength(self, nums: list[int]) -> int:
        n = len(nums)
        if n == 1:
            return 0
        for i in range(n - 2, -1, -1):
            if nums[i] >= nums[i + 1]:
                return i + 1
        return 0
# Time: O(n), Space: O(1)
```

<a id="wc486-q2"></a>
### Q2. [Rotate Non Negative Elements](https://leetcode.com/problems/rotate-non-negative-elements/) [M]

Description: Left-rotate only non-negative elements by k positions in-place.

Idea: Extract non-negative indices/values, rotate, write back.

```python
class Solution:
    def rotateElements(self, nums: list[int], k: int) -> list[int]:
        idx, vals = [], []
        for i, x in enumerate(nums):
            if x >= 0:
                idx.append(i)
                vals.append(x)
        if not vals:
            return nums
        k %= len(vals)
        rot = vals[k:] + vals[:k]
        for j, i in enumerate(idx):
            nums[i] = rot[j]
        return nums
# Time: O(n), Space: O(m) where m = non-negative count
```

<a id="wc486-q4"></a>
### Q4. [Find Nth Smallest Integer With K One Bits](https://leetcode.com/problems/find-nth-smallest-integer-with-k-one-bits/) [H]

Description: Return the n-th smallest non-negative integer with exactly k set bits.

Idea: Combinatorics — find MSB position via counting, then unrank remaining bits.

```python
class Solution:
    def nthSmallest(self, n: int, k: int) -> int:
        if k == 0:
            return 0
        CAP = n + 1

        def comb(a: int, b: int) -> int:
            if b < 0 or b > a:
                return 0
            b = min(b, a - b)
            res = 1
            for i in range(1, b + 1):
                res = res * (a - b + i) // i
                if res >= CAP:
                    return CAP
            return res

        # find MSB position p
        p = k - 1
        while True:
            cnt = comb(p, k - 1)
            if n > cnt:
                n -= cnt
                p += 1
            else:
                break

        ans = 1 << p
        r = k - 1
        for i in range(p - 1, -1, -1):
            if r == 0:
                break
            cnt0 = comb(i, r)
            if n > cnt0:
                ans |= 1 << i
                n -= cnt0
                r -= 1
        return ans
# Time: O(k * log(ans)), Space: O(1)
```
