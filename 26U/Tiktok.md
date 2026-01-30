## 以正合

## Category

### Strings
- [M] [5. 最长回文子串](#5-最长回文子串) — Expand around centers to track the longest palindromic substring.
- [M] [17. 电话号码的字母组合](#17-电话号码的字母组合) — Map digits to letter choices and backtrack the possible strings.
- [M] [22. 括号生成](#22-括号生成) — Grow valid parentheses by choosing when to place left/right brackets.
- [M] [79. 单词搜索](#79-单词搜索) — Backtracking search for a single word on a grid.
- [M] [93. 复原 IP 地址](#93-复原-ip-地址) — Split the string into four valid octets with pruning.

### Arrays & Hashing
- [M] [31. 下一个排列](#31-下一个排列) — Compute the lexicographically next permutation in place.
- [M] [75. 颜色分类](#75-颜色分类) — Dutch national flag partition to collect similar colors.
- [E] [88. 合并两个有序数组](#88-合并两个有序数组) — Merge into a sorted array using the spare tail of the first array.
- [M] [249. 移位字符串分组](#249-移位字符串分组) — Group shifted strings by their cyclic differences.

### Math & Geometry
- [M] [54. 螺旋矩阵](#54-螺旋矩阵) — Traverse a matrix in spiral order.
- [M] [59. 螺旋矩阵 II](#59-螺旋矩阵-ii) — Populate an n×n matrix in spiral order.
- [M] [2326. 螺旋矩阵 IV](#2326-螺旋矩阵-iv) — Fill a spiral matrix using a linked list stream.

### Two Pointers
- [E] [977. 有序数组的平方](#977-有序数组的平方) — Square and place values from the ends inward.
- [M] [360. 有序转化数组](#360-有序转化数组) — Apply a quadratic function and merge the two increasing halves.

### Backtracking
- [M] [39. 组合总和](#39-组合总和) — Find combinations that sum to the target while reusing candidates.
- [M] [40. 组合总和 II](#40-组合总和-ii) — Enumerate unique combinations without repeating the same index.
- [M] [46. 全排列](#46-全排列) — Standard backtracking generation of all permutations.
- [M] [47. 全排列 II](#47-全排列-ii) — Avoid duplicate permutations when numbers repeat.
- [M] [60. 排列序列](#60-排列序列) — Use factorial numbering to compute the k-th permutation directly.
- [M] [77. 组合](#77-组合) — Build k-element combinations from the first n numbers with DFS.
- [M] [78. 子集](#78-子集) — Enumerate every subset by choosing to include or skip each element.
- [M] [216. 组合总和 III](#216-组合总和-iii) — Choose k numbers from 1..9 that sum to n.
- [M] [254. 因子的组合](#254-因子的组合) — Factor n into products of integers greater than 1.
- [M] [784. 字母大小写全排列](#784-字母大小写全排列) — Toggle letter cases to generate every variant.

### Intervals
- [M] [56. 合并区间](#56-合并区间) — Merge overlapping intervals after sorting by start.

### 5. 最长回文子串
```python
class Solution:
    def longestPalindrome(self, s: str) -> str:
        n = len(s)
        ans_left = ans_right = 0

        for i in range(2 * n - 1):
            l, r = i // 2, (i + 1) // 2
            while l >= 0 and r < n and s[l] == s[r]:
                l -= 1
                r += 1
            # 循环结束后，s[l+1] 到 s[r-1] 是回文串
            if r - l - 1 > ans_right - ans_left:
                ans_left, ans_right = l + 1, r  # 左闭右开区间

        return s[ans_left: ans_right]


class Solution:
    def longestPalindrome(self, s: str) -> str:
        n = len(s)
        ans_left = ans_right = 0

        # 奇回文串
        for i in range(n):
            l = r = i
            while l >= 0 and r < n and s[l] == s[r]:
                l -= 1
                r += 1
            # 循环结束后，s[l+1] 到 s[r-1] 是回文串
            if r - l - 1 > ans_right - ans_left:
                ans_left, ans_right = l + 1, r  # 左闭右开区间

        # 偶回文串
        for i in range(n - 1):
            l, r = i, i + 1
            while l >= 0 and r < n and s[l] == s[r]:
                l -= 1
                r += 1
            if r - l - 1 > ans_right - ans_left:
                ans_left, ans_right = l + 1, r  # 左闭右开区间

        return s[ans_left: ans_right]
```

### 22. 括号生成
```python
class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        res = []
        def dfs(cur, open, close):
            if open == n and close == n:
                res.append(cur)
            if open < n:
                dfs(cur + "(", open + 1, close)
            if close < open:
                dfs(cur + ")", open, close + 1)
        dfs("", 0, 0)
        return res

class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        ans = []
        path = [''] * (n * 2)  
        def dfs(left: int, right: int) -> None:
            if right == n:  # 填完 2n 个括号
                ans.append(''.join(path))
                return
            if left < n:  # 可以填左括号
                path[left + right] = '('  # 直接覆盖
                dfs(left + 1, right)
            if right < left:  # 可以填右括号
                path[left + right] = ')'  # 直接覆盖
                dfs(left, right + 1)

        dfs(0, 0)
        return ans
```

### 17. 电话号码的字母组合
```python
class Solution:
    def letterCombinations(self, digits: str) -> List[str]:
        MAPPING = "", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"
        res = []
        def dfs(i, cur):
            if i == len(digits):
                res.append(cur)
                return
            for c in MAPPING[int(digits[i])]:
                cur += c
                dfs(i + 1, cur)
                cur = cur[:-1]
        dfs(0, "")
        return res

def letterCombinations(self, digits: str) -> List[str]:
    if not digits: return [] # Fix: Handle empty input
    MAPPING = "", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"
    res = []
    def dfs(i, cur):
        if i == len(digits):
            res.append("".join(cur)) # Join the list back into a string
            return
        # Fix: Get letters for the actual digit (e.g., '2' -> "abc")
        for c in MAPPING[int(digits[i])]: 
            cur.append(c) # List is mutable; we can append
            dfs(i + 1, cur)
            cur.pop()     # Now .pop() works
    dfs(0, []) # Start with an empty list
    return res

def letterCombinations(self, digits: str) -> List[str]:
    if not digits: return []
    MAPPING = "", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"
    res = []
    def dfs(i, cur):
        if i == len(digits):
            res.append(cur)
            return
        for c in MAPPING[int(digits[i])]:
            dfs(i + 1, cur + c)
    dfs(0, "")
    return res
```

### 93. 复原 IP 地址
```python
class Solution:
    def restoreIpAddresses(self, s: str) -> List[str]:
        if len(s) < 4 or len(s) > 12:
            return []
        res = []
        def backtrack(start_idx, path):
            if len(path) == 4:
                if start_idx == len(s):
                    res.append(".".join(path))
                return
            for length in range(1, 4):
                if start_idx + length > len(s):
                    break
                segment = s[start_idx : start_idx + length]
                if len(segment) > 1 and segment[0] == '0':
                    continue
                if int(segment) > 255:
                    continue
                path.append(segment)
                backtrack(start_idx + length, path)
                path.pop() # Backtrack
        backtrack(0, [])
        return res


class Solution:
    def restoreIpAddresses(self, s: str) -> List[str]:
        def is_valid(t: str) -> bool:
            # 长度不能超过 3，不能有前导零
            if len(t) > 3 or len(t) > 1 and t[0] == '0':
                return False
            return int(t) <= 255

        n = len(s)
        ans = []
        for i in range(1, n):
            if not is_valid(s[:i]):
                break
            for j in range(i + 1, n):
                if not is_valid(s[i:j]):
                    break
                for k in range(j + 1, n):
                    if not is_valid(s[j:k]):
                        break
                    if is_valid(s[k:]):
                        ans.append(f"{s[:i]}.{s[i:j]}.{s[j:k]}.{s[k:]}")
        return ans
```





### 31. 下一个排列
```python
[1, 5, 8, 4, 2]
[1, 8, 5, 4, 2]
[1, 8, 2, 4, 5]

class Solution:
    def nextPermutation(self, nums: List[int]) -> None:
        n = len(nums)
        i = n - 2
        while i >= 0 and nums[i] >= nums[i + 1]:
            i -= 1
        if i >= 0:
            j = n - 1
            while nums[i] >= nums[j]:
                j -= 1
            nums[i], nums[j] = nums[j], nums[i]
        l = i + 1
        r = n - 1
        while l < r:
            nums[l], nums[r] = nums[r], nums[l]
            l += 1
            r -= 1

class Solution:
    def nextPermutation(self, nums: List[int]) -> None:
        n = len(nums)

        # 第一步：从右向左找到第一个小于右侧相邻数字的数 nums[i]
        i = n - 2
        while i >= 0 and nums[i] >= nums[i + 1]:
            i -= 1

        # 如果找到了，进入第二步；否则跳过第二步，反转整个数组
        if i >= 0:
            # 第二步：从右向左找到 nums[i] 右边最小的大于 nums[i] 的数 nums[j]
            j = n - 1
            while nums[j] <= nums[i]:
                j -= 1
            # 交换 nums[i] 和 nums[j]
            nums[i], nums[j] = nums[j], nums[i]

        # 第三步：反转 nums[i+1:]（如果上面跳过第二步，此时 i = -1）
        # nums[i+1:] = nums[i+1:][::-1] 这样写也可以，但空间复杂度不是 O(1) 的
        left, right = i + 1, n - 1
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1
```

### 46. 全排列
```python
# visited
# range 0 - n, so it always get from 0, to pick all nums
class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        def dfs(cur):
            if len(cur) == len(nums):
                res.append(cur[:])
            else:
                for i in range(len(nums)):
                    if not visited[i]:
                        visited[i] = True
                        cur.append(nums[i])
                        dfs(cur)
                        cur.pop()
                        visited[i] = False
        visited = [False] * len(nums)
        res = []
        dfs([])
        return res

class Solution:
    def permute(self, nums):
        def backtrack(first = 0):
            if first == n:  
                res.append(nums[:])
            for i in range(first, n):
                nums[first], nums[i] = nums[i], nums[first]
                backtrack(first + 1)
                nums[first], nums[i] = nums[i], nums[first]
        n = len(nums)
        res = []
        backtrack()
        return res
```

### 47. 全排列 II
```python
"""
If visited[i-1] is True: You are currently in a branch where the first duplicate is already part of your permutation. It is safe to use the second one now.

If visited[i-1] is False: You already finished all possible permutations that start with the first duplicate. If you were to start a new branch with the second duplicate now, it would generate the exact same sequences. By skipping when visited[i-1] is False, you avoid this redundancy. """

# 2 conditions:
# 1. visited[index] is False 
# 2. nums[i] != nums[i-1] and visited[i-1] is True
# 保证先选第一个，然后从剩下的里面选
# 第二个看到前面的被选了，才可以被选上

class Solution:
    def permuteUnique(self, nums: List[int]) -> List[List[int]]:
        res = []
        nums.sort()  # Step 1: Sort to group duplicates
        visited = [False] * len(nums)

        def dfs(cur):
            if len(cur) == len(nums):
                res.append(cur[:])
                return
            for i in range(len(nums)):
                if visited[i]:
                    continue
                if i > 0 and nums[i] == nums[i-1] and not visited[i-1]:
                    continue
                visited[i] = True
                cur.append(nums[i])
                dfs(cur)
                cur.pop()
                visited[i] = False
        dfs([])
        return res

class Solution:
    def permuteUnique(self, nums: List[int]) -> List[List[int]]:
        nums.sort()
        n = len(nums)
        path = [0] * n  # 所有排列的长度都是 n
        on_path = [False] * n  # on_path[j] 表示 nums[j] 是否已经填入排列
        ans = []
        # i 表示当前要填排列的第几个数
        def dfs(i: int) -> None:
            if i == n:  # 填完了
                ans.append(path.copy())  # 也可以写 path[:]
                return
            # 枚举 nums[j] 填入 path[i]
            for j, on in enumerate(on_path):
                # 如果 nums[j] 已填入排列，continue
                # 如果 nums[j] 和前一个数 nums[j-1] 相等，且 nums[j-1] 没填入排列，continue
                if on or j > 0 and nums[j] == nums[j - 1] and not on_path[j - 1]:
                    continue
                path[i] = nums[j]  # 填入排列
                on_path[j] = True  # nums[j] 已填入排列（注意标记的是下标，不是值）
                dfs(i + 1)  # 填排列的下一个数
                on_path[j] = False  # 恢复现场
                # 注意 path 无需恢复现场，因为排列长度固定，直接覆盖 path[i] 就行
        dfs(0)
        return ans
```


### 77. 组合
```python
class Solution:
    def combine(self, n: int, k: int) -> List[List[int]]:
        res = []

        def dfs(start, cur):
            if len(cur) == k:
                res.append(cur[:])
                return
            for i in range(start, n + 1):
                cur.append(i)
                dfs(i + 1, cur)
                cur.pop()
        dfs(1, [])
        return res
```

### 78. 子集
```python
class Solution:
    def subsets(self, nums: List[int]) -> List[List[int]]:
        res = []
        def dfs(start, path):
            res.append(path[:])
            for i in range(start, len(nums)):
                path.append(nums[i])
                dfs(i + 1, path)
                path.pop()
        dfs(0, [])
        return res

class Solution:
    def subsets(self, nums: List[int]) -> List[List[int]]:
        n = len(nums)
        ans = []
        path = []
        def dfs(i: int) -> None:
            if i == n:  # 子集构造完毕
                ans.append(path.copy())  # 复制 path，也可以写 path[:]
                return
            dfs(i + 1)  # 考虑下一个数 nums[i+1] 选或不选
            path.append(nums[i])
            dfs(i + 1)  # 考虑下一个数 nums[i+1] 选或不选
            path.pop()  # 恢复现场，撤销 path.append(nums[i])
        dfs(0)
        return ans

```

### 39. 组合总和
```python
# reuse!
# binary tree
class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        # candidates.sort()
        res = []
        cur = []
        def dfs(i, rem):
            if rem == 0:
                res.append(cur[:])
                return
            if i == len(candidates) or rem < 0:
                return
            dfs(i + 1, rem)
            cur.append(candidates[i])
            dfs(i, rem - candidates[i])
            cur.pop()
        dfs(0, target)
        return res

# j-nary
class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        candidates.sort()
        res = []
        cur = []
        def dfs(i, rem):
            if rem == 0:
                res.append(cur[:])
                return
            for j in range(i, len(candidates)):
                if candidates[j] > rem:
                    break
                cur.append(candidates[j])
                dfs(j, rem - candidates[j])
                cur.pop()
        dfs(0, target)
        return res
```
### 40. 组合总和 II
```python
# 1, 1, 2
# i > start
# 1st round， 到第二个1， i = start, 不是> start, 所以pick
# 2st round， 第二个2 check against 1st 1, X
class Solution:
    def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:
        candidates.sort()
        res = []
        cur = []
        def dfs(start, rem):
            if rem == 0:
                res.append(cur[:])
                return

            for i in range(start, len(candidates)):
                if candidates[i] > rem:
                    continue
                if i > start and candidates[i] == candidates[i - 1]:
                    continue
                cur.append(candidates[i])
                dfs(i + 1, rem - candidates[i])
                cur.pop()
        dfs(0, target)
        return res

class Solution:
    def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:
        candidates.sort()
        n = len(candidates)
        ans = []
        path = []
        def dfs(i: int, left: int) -> None:
            if left == 0:
                ans.append(path.copy())  # 也可以写 path[:]
                return
            if i == n:
                return
            x = candidates[i]
            if left < x:
                return
            path.append(x)
            dfs(i + 1, left - x)
            path.pop()  # 恢复现场

            i += 1
            while i < n and candidates[i] == x:
                i += 1
            dfs(i, left)
        dfs(0, target)
        return ans


class Solution:
    def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:
        candidates.sort()
        res = []
        cur = []
        def dfs(i, rem):
            if rem == 0:
                res.append(cur[:])
                return
            for j in range(i, len(candidates)):
                if candidates[j] > rem:
                    break
                if j > i and candidates[j] == candidates[j - 1]:
                    continue
                cur.append(candidates[j])
                dfs(j + 1, rem - candidates[j])
                cur.pop()
        dfs(0, target)
        return res
```

### 216. 组合总和 III
```python
class Solution:
    def combinationSum3(self, k: int, n: int) -> List[List[int]]:
        res = []
        cur = []
        def dfs(start, rem):
            if rem == 0 and len(cur) == k:
                res.append(cur[:])
                return
            for i in range(start, 10):
                if i > rem:
                    continue
                cur.append(i)
                dfs(i + 1, rem - i)
                cur.pop()
        dfs(1, n)
        return res

class Solution:
    def combinationSum3(self, k: int, n: int) -> List[List[int]]:
        res = []
        cur = []
        def dfs(start, l, rem):
            if l < 0:
                return
            if rem == 0 and l == 0:
                res.append(cur[:])
                return
            for i in range(start, 10):
                if i > rem:
                    continue
                cur.append(i)
                dfs(i + 1, l - 1, rem - i)
                cur.pop()
        dfs(1, k, n)
        return res
```

### 254. 因子的组合
```python
# don't return, keep going
# dfs also satrt with i, reuse
# target // i, path = [... i] + [target]
class Solution:
    def getFactors(self, n: int) -> List[List[int]]:
        res = []
        def dfs(target, start, path):
            if path:
                res.append(path + [target])
            for i in range(start, int(math.sqrt(target)) + 1):
                if target % i == 0:
                    path.append(i)
                    dfs(target // i, i, path) # reuse i
                    path.pop()
        dfs(n, 2, [])
        return res
```


### 60. 排列序列
```python
import math

def getPermutation(self, n: int, k: int) -> str:
    # 1. Create a list of numbers [1, 2, ..., n]
    nums = [str(i) for i in range(1, n + 1)]
    
    # 2. Precompute (n-1)!
    fact = math.factorial(n - 1)
    
    # 3. Use 0-based indexing for k
    k -= 1
    res = []
    
    for i in range(n - 1, 0, -1):
        # Determine the index of the next digit
        idx = k // fact
        res.append(nums.pop(idx))
        
        # Update k and the factorial for the next round
        k %= fact
        fact //= i
        
    # Append the last remaining number
    res.append(nums[0])
    return "".join(res)
```    

### 784. 字母大小写全排列
```python
class Solution:
    def letterCasePermutation(self, s: str) -> List[str]:
        ans = []
        def dfs(s: List[str], pos: int) -> None:
            while pos < len(s) and s[pos].isdigit():
                pos += 1
            if pos == len(s):
                ans.append(''.join(s))
                return
            dfs(s, pos + 1)
            s[pos] = s[pos].swapcase()
            dfs(s, pos + 1)
            s[pos] = s[pos].swapcase()
        dfs(list(s), 0)
        return ans

class Solution:
    def letterCasePermutation(self, s: str) -> List[str]:
        ans = []
        q = deque([''])
        while q:
            cur = q[0]
            pos = len(cur)
            if pos == len(s):
                ans.append(cur)
                q.popleft()
            else:
                if s[pos].isalpha():
                    q.append(cur + s[pos].swapcase())
                q[0] += s[pos]
        return ans
```

### 54. 螺旋矩阵
```python
class Solution:
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        DIR = (0, 1), (1, 0), (0, -1), (-1, 0)
        m, n = len(matrix), len(matrix[0])
        res = []
        i = j = di = 0
        for _ in range(m * n):
            res.append(matrix[i][j])
            matrix[i][j] = None
            x, y = i + DIR[di][0], j + DIR[di][1]
            if x < 0 or x >= m or y < 0 or y >= n or matrix[x][y] is None:
                di = (di + 1) % 4
            i += DIR[di][0]
            j += DIR[di][1]
        return res

class Solution:
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        DIR = (0, 1), (1, 0), (0, -1), (-1, 0)
        m, n = len(matrix), len(matrix[0])
        res = []
        i, j, di = 0, -1, 0
        ttl = m*n
        while len(res) < ttl:
            dx, dy = DIR[di]
            for _ in range(n):
                i += dx
                j += dy
                res.append(matrix[i][j])
            di = (di + 1) % 4
            n, m = m - 1, n
        return res
```

### 59. 螺旋矩阵 II
```python
class Solution:
    def generateMatrix(self, n: int) -> List[List[int]]:
        DIR = (0, 1), (1, 0), (0, -1), (-1, 0)
        i = j = di = 0
        res = [[0] * n for _ in range(n)]
        for val in range(1, n*n + 1):
            res[i][j] =val
            x, y = i + DIR[di][0], j + DIR[di][1]
            if x < 0 or x >= n or y < 0 or y >= n or res[x][y]:
                di = (di + 1) % 4
            i += DIR[di][0]
            j += DIR[di][1]
        return res
```

### 2326. 螺旋矩阵 IV
```python
class Solution:
    def spiralMatrix(self, m: int, n: int, head: Optional[ListNode]) -> List[List[int]]:
        DIR = (0, 1), (1, 0), (0, -1), (-1, 0)
        res = [[-1] * n for _ in range(m)]
        i = j = di = 0
        while head:
            res[i][j] = head.val
            head = head.next
            x, y = i + DIR[di][0], j + DIR[di][1]
            if x < 0 or x >= m or y < 0 or y >= n or res[x][y] is not -1:
                di = (di + 1) % 4
            i += DIR[di][0]
            j += DIR[di][1]
        return res
```

### 75. 颜色分类
```python

```



### 249. 移位字符串分组
```python
class Solution:
    def groupStrings(self, strings: List[str]) -> List[List[str]]:
        res = []
        dc = defaultdict(list)
        for s in strings:
            key = []
            for i in range(1, len(s)):
                key.append((ord(s[i]) - ord(s[i - 1])) % 26) 
            dc[tuple(key)].append(s)
        return list(dc.values())
```


### 79. 单词搜索
```python



```


### 88. 合并两个有序数组
```python
class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        p1, p2, p = m - 1, n - 1, m + n - 1
        while p2 >= 0:
            if p1 >= 0 and nums1[p1] > nums2[p2]:
                nums1[p] = nums1[p1]
                p1 -= 1
            else:
                nums1[p] = nums2[p2]
                p2 -= 1
            p -= 1

# l2 left, l1 exhausted
class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        l1 = m - 1
        l2 = n - 1
        end = m + n - 1
        while l1 >= 0 and l2 >= 0:
            if nums2[l2] > nums1[l1]:
                nums1[end] = nums2[l2]
                l2 -= 1
            else:
                nums1[end] = nums1[l1]
                l1 -= 1
            end -= 1
        if l1 < 0:
            nums1[:l2 + 1] = nums2[:l2 + 1]
```

### 977. 有序数组的平方
```python
class Solution:
    def sortedSquares(self, nums: List[int]) -> List[int]:
        n = len(nums)
        ans = [0] * n
        i, j = 0, n - 1
        for p in range(n - 1, -1, -1):
            x = nums[i] * nums[i]
            y = nums[j] * nums[j]
            if x > y:  # 更大的数放右边
                ans[p] = x
                i += 1
            else:
                ans[p] = y
                j -= 1
        return ans
```
### 360. 有序转化数组
```python
def sortTransformedArray(nums: List[int], a: int, b: int, c: int) -> List[int]:
    def f(x):
        return a * x * x + b * x + c
    n = len(nums)
    result = [0] * n
    left, right = 0, n - 1
    # If a >= 0, largest values are at edges; fill result from the end
    # If a < 0, smallest values are at edges; fill result from the start
    curr = n - 1 if a >= 0 else 0
    
    while left <= right:
        val_l, val_r = f(nums[left]), f(nums[right])
        if a >= 0:
            if val_l > val_r:
                result[curr] = val_l
                left += 1
            else:
                result[curr] = val_r
                right -= 1
            curr -= 1 # Move toward the front
        else:
            if val_l < val_r:
                result[curr] = val_l
                left += 1
            else:
                result[curr] = val_r
                right -= 1
            curr += 1 # Move toward the back
            
    return result
```


### 56. 合并区间
```python
class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        intervals.sort()
        merged = []
        for itv in intervals:
            if not merged or merged[-1][1] < itv[0]:
                merged.append(itv)
            else:
                merged[-1][1] = max(merged[-1][1], itv[1])
        return merged
```


