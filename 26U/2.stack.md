# Stack

## Category

### Easy
- [E] [496. Next Greater Element I](#lc-0496) \
  For each element in `nums1`, return the next greater value to its right in `nums2`. \
  `Stack` `Monotonic Stack` `Hash Table`

- [E] [1475. Final Prices With a Special Discount in a Shop](#lc-1475) \
  Subtract the first smaller-or-equal future price from each price to compute the discounted result. \
  `Stack` `Monotonic Stack` `Array`

### Medium
- [M] [739. Daily Temperatures](#lc-0739) \
  For every day find how many days until a warmer temperature using a next-greater-day stack. \
  `Stack` `Monotonic Stack` `Array`

- [M] [402. Remove K Digits](#lc-0402) \
  Drop digits greedily whenever a larger digit precedes a smaller one until `k` removals finish, then trim leading zeros. \
  `Stack` `Greedy` `String`

- [M] [1673. Find the Most Competitive Subsequence](#lc-1673) \
  Maintain a stack-sized `k` while evicting larger values whenever enough elements remain to fulfill the length constraint. \
  `Stack` `Greedy` `Array`

- [M] [738. Monotone Increasing Digits](#lc-0738) \
  Scan from right to left, lower digits when needed, then fill the suffix with 9s so the result stays maximal but non-decreasing. \
  `Monotonic Stack` `Greedy` `Math`

- [M] [2259. Remove Digit From Number to Maximize Result](#lc-2259) \
  Remove the first occurrence of the target digit that is followed by a larger neighbor, or drop the final occurrence when none exists. \
  `Greedy` `String`

- [M] [316. Remove Duplicate Letters](#lc-0316) \
  Build the lexicographically smallest subsequence that contains each letter once by monitoring future availability counts. \
  `Stack` `Greedy` `String`

- [M] [1504. Count Submatrices With All Ones](#lc-1504) \
  Treat each row as a histogram of consecutive ones and use a monotonic stack to count rectangles ending at the current row. \
  `Stack` `Dynamic Programming` `Matrix`

- [M] [503. Next Greater Elements II](#lc-0503) \
  Sweep the array twice to assign each index the first greater value wrapping around once. \
  `Stack` `Monotonic Stack` `Circular Array`

- [M] [556. Next Greater Element III](#lc-0556) \
  Compute the next permutation by locating the first descent, swapping with the next bigger digit, and reversing the suffix. \
  `Stack` `Greedy` `Math`

## Solutions (Python)

<a id="lc-0496"></a>
#### 496. [Next Greater Element I](https://leetcode.com/problems/next-greater-element-i/) [E]
`Stack` `Monotonic Stack` `Hash Table`
Description: Map every entry in `nums2` to its next greater neighbor, then lookup `nums1`.

##### Approach: Decreasing stack + hashmap
Idea: Sweep `nums2` while keeping a decreasing stack, record each popped value's next greater element, and answer each `nums1` query.

```python
class Solution:
    def nextGreaterElement(self, nums1: List[int], nums2: List[int]) -> List[int]:
        d = {}
        stack = []
        for x in nums2:
            while stack and stack[-1] < x:
                d[stack.pop()] = x
            stack.append(x)
        return [d.get(x, -1) for x in nums1]
# Time: O(len(nums1) + len(nums2)), Space: O(len(nums2))
```

##### Approach: Index stack on `nums2`
Idea: Store indices to fill answers for previous elements as soon as a greater value arrives, then reuse the same map.

```python
class Solution:
    def nextGreaterElement(self, nums1: List[int], nums2: List[int]) -> List[int]:
        d = {}
        stack = []
        for i, x in enumerate(nums2):
            while stack and nums2[stack[-1]] < x:
                idx = stack.pop()
                d[nums2[idx]] = x
            stack.append(i)
        return [d.get(x, -1) for x in nums1]
# Time: O(len(nums1) + len(nums2)), Space: O(len(nums2))
```

<a id="lc-1475"></a>
#### 1475. [Final Prices With a Special Discount in a Shop](https://leetcode.com/problems/final-prices-with-a-special-discount-in-a-shop/) [E]
`Stack` `Monotonic Stack` `Array`
Description: Use a monotonic stack to subtract the next smaller-or-equal price from each price in place.

##### Approach: Index stack for discounts
Idea: Push indices with unresolved discounts, pop whenever a smaller price arrives, and reduce the recorded price.

```python
class Solution:
    def finalPrices(self, prices: List[int]) -> List[int]:
        stack = []
        for i, price in enumerate(prices):
            while stack and prices[stack[-1]] >= price:
                idx = stack.pop()
                prices[idx] -= price
            stack.append(i)
        return prices
# Time: O(len(prices)), Space: O(len(prices))
```

##### Approach: Reverse scan maintaining candidate discounts
Idea: Walk from right to left, keep the smallest seen price in a stack so each entry can subtract the next available discount.

```python
class Solution:
    def finalPrices(self, prices: List[int]) -> List[int]:
        res = prices[:]
        stack = []
        for i in range(len(prices) - 1, -1, -1):
            price = prices[i]
            while stack and stack[-1] > price:
                stack.pop()
            if stack:
                res[i] -= stack[-1]
            stack.append(price)
        return res
# Time: O(len(prices)), Space: O(len(prices))
```

<a id="lc-0739"></a>
#### 739. [Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) [M]
`Stack` `Monotonic Stack` `Array`
Description: For every day, report how many days until a warmer temperature using a monotonic index stack.

##### Approach: Next greater temperature stack
Idea: Maintain a stack of indices with decreasing temperatures so each new warmer day resolves earlier entries.

```python
class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        n = len(temperatures)
        stack = []
        res = [0] * n
        for i, temp in enumerate(temperatures):
            while stack and temp > temperatures[stack[-1]]:
                prev = stack.pop()
                res[prev] = i - prev
            stack.append(i)
        return res
# Time: O(n), Space: O(n)
```

<a id="lc-0402"></a>
#### 402. [Remove K Digits](https://leetcode.com/problems/remove-k-digits/) [M]
`Stack` `Greedy` `String`
Description: Greedily drop digits that make the prefix larger and trim leading zeros after `k` removals.

##### Approach: Monotonic digit stack
Idea: Maintain an increasing stack of digits, drop while the current digit is smaller and remaining removals exist, then strip zeros.

```python
class Solution:
    def removeKdigits(self, num: str, k: int) -> str:
        stack = []
        for digit in num:
            while stack and k > 0 and stack[-1] > digit:
                stack.pop()
                k -= 1
            stack.append(digit)
        final = stack[:-k] if k else stack
        return ''.join(final).lstrip('0') or '0'
# Time: O(len(num)), Space: O(len(num))
```

<a id="lc-1673"></a>
#### 1673. [Find the Most Competitive Subsequence](https://leetcode.com/problems/find-the-most-competitive-subsequence/) [M]
`Stack` `Greedy` `Array`
Description: Build the lexicographically smallest subsequence of length `k` by popping larger elements whenever enough remain to fill the target.

##### Approach: Greedy stack with remaining budget
Idea: Track how many elements can be removed and always drop the stack top if it is larger than the current element and we can still reach length `k`.

```python
class Solution:
    def mostCompetitive(self, nums: List[int], k: int) -> List[int]:
        stack = []
        can_remove = len(nums) - k
        for x in nums:
            while stack and can_remove > 0 and stack[-1] > x:
                stack.pop()
                can_remove -= 1
            stack.append(x)
        return stack[:k]
# Time: O(len(nums)), Space: O(len(nums))
```

##### Approach: Stack with lookahead count
Idea: Keep track of how many elements remain, ensuring that we can still push a value if the stack lacks `k` elements.

```python
class Solution:
    def mostCompetitive(self, nums: List[int], k: int) -> List[int]:
        stack = []
        for i, x in enumerate(nums):
            while stack and x < stack[-1] and len(stack) + len(nums) - i > k:
                stack.pop()
            if len(stack) < k:
                stack.append(x)
        return stack
# Time: O(len(nums)), Space: O(len(nums))
```

<a id="lc-0738"></a>
#### 738. [Monotone Increasing Digits](https://leetcode.com/problems/monotone-increasing-digits/) [M]
`Monotonic Stack` `Greedy` `Math`
Description: When a digit violates the non-decreasing order, decrement it and set all later digits to 9 to maximize the value.

##### Approach: Right-to-left adjustment
Idea: Scan digits from right to left, mark where decreases occur, decrement the offending digit, then replace the suffix with 9s.

```python
class Solution:
    def monotoneIncreasingDigits(self, n: int) -> int:
        digits = list(str(n))
        flag = len(digits)
        for i in range(len(digits) - 1, 0, -1):
            if digits[i - 1] > digits[i]:
                digits[i - 1] = str(int(digits[i - 1]) - 1)
                flag = i
        for i in range(flag, len(digits)):
            digits[i] = '9'
        return int(''.join(digits))
# Time: O(log n), Space: O(log n)
```

<a id="lc-2259"></a>
#### 2259. [Remove Digit From Number to Maximize Result](https://leetcode.com/problems/remove-digit-from-number-to-maximize-result/) [M]
`Greedy` `String`
Description: Remove the leftmost target digit that is followed by a larger digit to maximize the remaining number.

##### Approach: Greedy one-pass removal
Idea: Track the final occurrence of the target, but return immediately when a removable digit is followed by a larger neighbor.

```python
class Solution:
    def removeDigit(self, number: str, digit: str) -> str:
        last = -1
        for i, c in enumerate(number):
            if c == digit:
                last = i
                if i < len(number) - 1 and number[i] < number[i + 1]:
                    return number[:i] + number[i + 1:]
        return number[:last] + number[last + 1:]
# Time: O(len(number)), Space: O(len(number))
```

<a id="lc-0316"></a>
#### 316. [Remove Duplicate Letters](https://leetcode.com/problems/remove-duplicate-letters/) [M]
`Stack` `Greedy` `String`
Description: Keep a monotonic stack of characters, ensuring each letter appears once while maintaining lexicographic order.

##### Approach: Counter-aware stack
Idea: Use `Counter` to know whether a letter reappears; pop from the stack while the next letter is smaller and still available later.

```python
from collections import Counter

class Solution:
    def removeDuplicateLetters(self, s: str) -> str:
        stack = []
        counter = Counter(s)
        for ch in s:
            counter[ch] -= 1
            if ch in stack:
                continue
            while stack and ch < stack[-1] and counter[stack[-1]] > 0:
                stack.pop()
            stack.append(ch)
        return ''.join(stack)
# Time: O(len(s)), Space: O(1)
```

<a id="lc-1504"></a>
#### 1504. [Count Submatrices With All Ones](https://leetcode.com/problems/count-submatrices-with-all-ones/) [M]
`Stack` `Dynamic Programming` `Matrix`
Description: For each row, treat the prefix of ones as heights and count rectangles ending at that row with a monotonic stack.

##### Approach: Histogram stacking per row
Idea: Build histograms of consecutive ones for each row, then use a monotonic stack to sum rectangle counts ending at each column.

```python
class Solution:
    def numSubmat(self, mat: List[List[int]]) -> int:
        if not mat or not mat[0]:
            return 0
        n = len(mat[0])
        heights = [0] * n
        res = 0
        for row in mat:
            stack = []
            total = 0
            for j, val in enumerate(row):
                heights[j] = heights[j] + 1 if val else 0
                count = 1
                while stack and stack[-1][0] >= heights[j]:
                    h, c = stack.pop()
                    total -= h * c
                    count += c
                stack.append((heights[j], count))
                total += heights[j] * count
                res += total
        return res
# Time: O(m * n), Space: O(n)
```

<a id="lc-0503"></a>
#### 503. [Next Greater Elements II](https://leetcode.com/problems/next-greater-element-ii/) [M]
`Stack` `Monotonic Stack` `Circular Array`
Description: Treat the array as circular by scanning twice (or reversing) so each position finds its next greater value.

##### Approach: Two-pass stack over doubled range
Idea: Iterate `2n` steps, pushing indices the first time and resolving them whenever a larger value appears in the doubled loop.

```python
class Solution:
    def nextGreaterElements(self, nums: List[int]) -> List[int]:
        n = len(nums)
        res = [-1] * n
        stack = []
        for i in range(2 * n):
            idx = i % n
            while stack and nums[idx] > nums[stack[-1]]:
                res[stack.pop()] = nums[idx]
            if i < n:
                stack.append(i)
        return res
# Time: O(n), Space: O(n)
```

##### Approach: Reverse circular stack
Idea: Process from right to left, keeping a stack of candidate greater values so each index can peek at the next larger number without extra modulo math.

```python
class Solution:
    def nextGreaterElements(self, nums: List[int]) -> List[int]:
        n = len(nums)
        stack = []
        ans = [-1] * n
        for i in range(2 * n - 1, -1, -1):
            x = nums[i % n]
            while stack and x >= stack[-1]:
                stack.pop()
            if i < n and stack:
                ans[i] = stack[-1]
            stack.append(x)
        return ans
# Time: O(n), Space: O(n)
```

<a id="lc-0556"></a>
#### 556. [Next Greater Element III](https://leetcode.com/problems/next-greater-element-iii/) [M]
`Stack` `Greedy` `Math`
Description: Generate the next higher permutation by finding the first descent, swapping with the next bigger digit, and reversing the suffix.

##### Approach: Next permutation pattern
Idea: Identify the pivot where digits decrease, swap with the smallest greater digit to the right, and reverse the suffix to get the smallest larger number.

```python
class Solution:
    def nextGreaterElement(self, n: int) -> int:
        nums = list(str(n))
        i = len(nums) - 2
        while i >= 0 and nums[i] >= nums[i + 1]:
            i -= 1
        if i == -1:
            return -1
        j = len(nums) - 1
        while nums[i] >= nums[j]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
        nums[i + 1:] = nums[i + 1:][::-1]
        res = int(''.join(nums))
        return res if res < 2**31 else -1
# Time: O(log n), Space: O(log n)
```
