## 以正合

## Index

### Strings
- [M] [5. 最长回文子串](#5-最长回文子串) \
  Expand around every center (odd/even) to track the longest palindrome. \
  `String` `Two Pointers`

- [M] [17. 电话号码的字母组合](#17-电话号码的字母组合) \
  Map digits to letter groups and backtrack over choices at each position. \
  `String` `Backtracking` `Mapping`

- [M] [22. 括号生成](#22-括号生成) \
  Backtrack by adding '(' when available and ')' when valid to build well-formed sequences. \
  `String` `Backtracking`

- [M] [79. 单词搜索](#79-单词搜索) \
  DFS through the board, marking visited cells to trace the input word sequentially. \
  `Matrix` `Backtracking` `DFS`

- [M] [93. 复原 IP 地址](#93-复原-ip-地址) \
  Backtrack through four segments, pruning invalid octets and leading zeros early. \
  `String` `Backtracking` `Validation`

### Arrays & Hashing
- [M] [31. 下一个排列](#31-下一个排列) \
  Scan from the end to find the first decrease, swap with the next larger value, then reverse the suffix. \
  `Array` `Greedy` `Two Pointers`

- [M] [75. 颜色分类](#75-颜色分类) \
  Partition colors by swapping zeros to the left and twos to the right in a single pass. \
  `Array` `Two Pointers` `In-Place`

- [E] [88. 合并两个有序数组](#88-合并两个有序数组) \
  Merge from the back so the larger elements shift right without overwriting unprocessed values. \
  `Array` `Two Pointers` `In-Place`

- [M] [249. 移位字符串分组](#249-移位字符串分组) \
  Normalize cyclic differences between adjacent letters to group shifted strings. \
  `String` `Hash Table` `Grouping`

### Math & Geometry
- [M] [54. 螺旋矩阵](#54-螺旋矩阵) \
  Simulate spiral traversal by marking visited cells and switching direction when needed. \
  `Array` `Matrix` `Simulation`

- [M] [59. 螺旋矩阵 II](#59-螺旋矩阵-ii) \
  Fill an n×n matrix in spiral order by rotating through four directions as you assign consecutive values. \
  `Array` `Matrix` `Simulation`

- [M] [2326. 螺旋矩阵 IV](#2326-螺旋矩阵-iv) \
  Stream nodes into a spiral matrix, rotating directions and stopping when the list runs out. \
  `Linked List` `Matrix` `Simulation`

### Two Pointers
- [E] [977. 有序数组的平方](#977-有序数组的平方) \
  Square values from both ends and fill the output backwards to keep results sorted. \
  `Array` `Two Pointers` `Math`

- [M] [360. 有序转化数组](#360-有序转化数组) \
  Apply two pointers to place transformed values in order, handling parabolas opening up/down separately. \
  `Array` `Two Pointers` `Math`

### Backtracking
- [M] [39. 组合总和](#39-组合总和) \
  Reuse candidates recursively while tracking the remaining sum to build valid combinations. \
  `Backtracking` `DFS`

- [M] [40. 组合总和 II](#40-组合总和-ii) \
  Sort candidates and skip duplicates during DFS to avoid repeated combination sets. \
  `Backtracking` `DFS` `Dedup`

- [M] [46. 全排列](#46-全排列) \
  Use visited tracking to explore each unused number and collect full-length permutations. \
  `Backtracking` `DFS`

- [M] [47. 全排列 II](#47-全排列-ii) \
  Sort and skip duplicates by checking previous elements to avoid repeating permutations. \
  `Backtracking` `DFS`

- [M] [60. 排列序列](#60-排列序列) \
  Use factorial numbering to select digits one-by-one for the k-th permutation. \
  `Math` `Permutation` `Factorial Number`

- [M] [77. 组合](#77-组合) \
  DFS from each start value to gather k-number combinations using pruning when size reaches k. \
  `Backtracking` `DFS` `Combinatorics`

- [M] [78. 子集](#78-子集) \
  Recurse by choosing to include or skip each element, collecting every subset along the way. \
  `Backtracking` `DFS`

- [M] [216. 组合总和 III](#216-组合总和-iii) \
  Choose k distinct digits from 1..9 via constrained DFS so their sum equals n. \
  `Backtracking` `DFS` `Combinatorics`

- [M] [254. 因子的组合](#254-因子的组合) \
  Try divisors up to sqrt(n) and recurse with the quotient to collect factor combinations. \
  `Math` `Backtracking` `DFS`

- [M] [267. 回文排列 II](#267-回文排列-ii) \
  Build palindromic halves by using characters in pairs and inserting the odd center when needed. \
  `Backtracking` `DFS` `Palindrome`

- [M] [784. 字母大小写全排列](#784-字母大小写全排列) \
  Toggle letter cases recursively whenever a letter is encountered to build all variants. \
  `Backtracking` `String` `DFS`

### Intervals
- [M] [56. 合并区间](#56-合并区间) \
  Sort intervals by start and merge overlaps by extending the end when necessary. \
  `Array` `Intervals` `Sorting`

### Dynamic Programming
- [M] [516. 最长回文子序列](#516-最长回文子序列) \
  用 DP 记录每个子串的最⻓回文子序列长度并向外扩展。 \
  `String` `Dynamic Programming`

- [M] [647. 回文子串](#647-回文子串) \
  对每个中心扩展或用 DP 表统计回文区间数。 \
  `String` `Dynamic Programming` `Center Expansion`

- [M] [55. 跳跃游戏](#55-跳跃游戏) \
  贪心追踪最远可达位置，判断是否能到达末尾。 \
  `Array` `Greedy` `Dynamic Programming`

- [H] [337. 打家劫舍 III](#337-打家劫舍-iii) \
  树形 DP 决定抢或不抢每个节点来最大化收益。 \
  `Tree` `DFS` `Dynamic Programming`

- [M] [53. 最大子数组和](#53-最大子数组和) \
  Kadane 或 DP 维护当前与全局最大子数组和。 \
  `Array` `Dynamic Programming`

- [M] [628. 三个数的最大乘积](#628-三个数的最大乘积) \
  排序后比较最大三数与两个最小一最大组合的乘积。 \
  `Array` `Math`

- [M] [238. 除了自身以外数组的乘积](#238-除了自身以外数组的乘积) \
  前缀与后缀乘积构造每个元素的答案，避开除法。 \
  `Array` `Dynamic Programming`

- [M] [256. 粉刷房子](#256-粉刷房子) \
  记录三种颜色的最小费用，按层级转移。 \
  `Dynamic Programming` `Matrix`

- [M] [276. 栅栏涂色](#276-栅栏涂色) \
  DP/组合公式计算相邻不同颜色的合法方案数。 \
  `Dynamic Programming` `Math`

- [M] [740. 删除并获得点数](#740-删除并获得点数) \
  将值映射到点数，转化为打家劫舍求最大值。 \
  `Array` `Dynamic Programming` `Hash Table`

- [M] [2611. 老鼠和奶酪](#2611-老鼠和奶酪) \
  按奶酪增益排序，先选收益最大的 k 份给第一只老鼠。 \
  `Greedy` `Sorting`

### 5. 最长回文子串
`String` `Two Pointers` \
Expand around every center (odd/even) to track the longest palindrome.

```python
# center expansion with memoization
class Solution:
    def longestPalindrome(self, s: str) -> str:
        @cache
        def isP(i, j):
            if i >= j:
                return True
            return s[i] == s[j] and isP(i + 1, j - 1)

        begin = 0
        mxL = 1
        n = len(s)
        for i in range(n):
            for j in range(i + mxL, n):
                if isP(i, j):
                    mxL = j - i + 1
                    begin = i
        return s[begin: begin + mxL]

class Solution:
    def longestPalindrome(self, s: str) -> str:
        @cache
        def expand(s, l, r):
            while l >= 0 and r < len(s) and s[l] == s[r]:
                l -= 1
                r += 1
            return l + 1, r - 1
        start = end = 0
        for i in range(len(s)):
            l1, r1 = expand(s, i, i)
            l2, r2 = expand(s, i, i + 1)
            if r1 - l1 > end - start:
                start, end = l1, r1
            if r2 - l2 > end - start:
                start, end = l2, r2
        return s[start: end + 1]


# dp
class Solution:
    def longestPalindrome(self, s: str) -> str:
        n = len(s)
        if n < 2: return s
        begin = 0
        mxL = 1
        dp = [[False] * n for _ in range(n)]
        for i in range(n):
            dp[i][i] = True
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                if s[i] == s[j]:
                    if j - i < 3:
                        dp[i][j] = True
                    else:
                        dp[i][j] = dp[i+1][j-1]
                    if dp[i][j] and (j - i + 1) > mxL:
                        mxL = max(mxL, j - i + 1)
                        begin = i
        return s[begin: begin + mxL]


# center, for both odd and even
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

# odd/even center
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

# brute force
# j in i, n
# j - i + 1
# sub = s[i:j+1]    get the last index
class Solution:
    def longestPalindrome(self, s: str) -> str:
        n = len(s)
        mx = 0
        res = ""
        for i in range(n):
            for j in range(i, n):
                sub = s[i:j+1]
                if sub == sub[::-1]:
                    if j-i+1> mx:
                        mx = max(mx, j-i+1)
                        res = sub
        return res

# j - i
for i in range(n):
    for j in range(i + 1, n + 1): 
        sub = s[i:j]
        if sub == sub[::-1]:
            if (j - i) > mx:
                mx = j - i
                res = sub
```

### 131. 分割回文串
`String` `Backtracking` `DFS`
```python
# backtrack with memoization
class Solution:
    def partition(self, s: str) -> List[List[str]]:
        n = len(s)
        res = []
        cur = []
        @cache
        def isP(i, j):
            if i >= j:
                return True
            return s[i] == s[j] and isP(i+1,j-1)
        def dfs(i):
            if i == n:
                res.append(cur[:])
                return
            for j in range(i, n):
                if isP(i, j):
                    cur.append(s[i: j+1])
                    dfs(j + 1)
                    cur.pop()
        dfs(0)
        return res

# dfs(i)
# for i in (i, n)
class Solution:
    def partition(self, s: str) -> List[List[str]]:
        n = len(s)
        res = []
        cur = []
        def dfs(i):
            if i == n:
                res.append(cur[:])
                return
            for j in range(i, n):
                t = s[i:j+1]
                if t == t[::-1]:
                    cur.append(t)
                    dfs(j + 1)
                    cur.pop()
        dfs(0)
        return res


# dfs(start, i + 1)
# dfs(i + 1, i + 1)   start = i + 1   append s[start: i + 1]
class Solution:
    def partition(self, s: str) -> List[List[str]]:
        n = len(s)
        res = []
        cur = []
        def dfs(start, i):
            if i == n:
                res.append(cur[:])
                return
            if i < n - 1:
                dfs(start, i + 1)
            t = s[start: i + 1]
            if t == t[::-1]:
                cur.append(t)
                dfs(i + 1, i + 1)
                cur.pop()
        dfs(0, 0)
        return res

# dp[]
class Solution:
    def partition(self, s: str) -> List[List[str]]:
        n = len(s)
        
        # 1. Precompute Palindromes using a 2D table (O(N^2))
        # This makes checking s[j:i] a O(1) operation
        is_pal = [[False] * n for _ in range(n)]
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                if s[i] == s[j] and (j - i < 3 or is_pal[i + 1][j - 1]):
                    is_pal[i][j] = True
        
        # 2. DP Tabulation: dp[i] stores all partitions for s[0:i]
        dp = [[] for _ in range(n + 1)]
        dp[0] = [[]] # Base case
        
        for i in range(1, n + 1):
            # Check every potential "last cut" at index j
            for j in range(i):
                # If the tail s[j:i] is a palindrome
                if is_pal[j][i - 1]:
                    # Extend all partitions of the prefix s[0:j]
                    for part in dp[j]:
                        dp[i].append(part + [s[j:i]])
                        
        return dp[n]
```

### 516. 最长回文子序列
`String` `Dynamic Programming` \
Use DP to track longest palindromic subsequences in substrings, building up from length 1 to n.
```python
# 'aa'
# dp[i+1][j-1] = dp[1][0] = 0
# the tabulation is all 0, not just i++ j++
class Solution:
    def longestPalindromeSubseq(self, s: str) -> int:
        n = len(s)
        dp = [[0] * n for _ in range(n)]
        for i in range(n):
            dp[i][i] = 1
        for i in range(n - 1, -1, -1):
            for j in range(i + 1, n):
                if s[i] == s[j]:
                    dp[i][j] = dp[i+1][j-1] + 2
                else:
                    dp[i][j] = max(dp[i+1][j], dp[i][j-1])
        return dp[0][n-1]

class Solution:
    def longestPalindromeSubseq(self, s: str) -> int:
        @cache  # 缓存装饰器，避免重复计算 dfs 的结果（记忆化）
        def dfs(i: int, j: int) -> int:
            if i > j:
                return 0  # 空串
            if i == j:
                return 1  # 只有一个字母
            if s[i] == s[j]:
                return dfs(i + 1, j - 1) + 2  # 都选
            return max(dfs(i + 1, j), dfs(i, j - 1))  # 枚举哪个不选
        return dfs(0, len(s) - 1)
```



### 647. 回文子串
`String` `Backtracking` `DP` \
Count palindromic substrings by expanding around centers or using DP to track valid palindromes.

```python
# two pointers
# i, i    i, i+1
class Solution:
    def countSubstrings(self, s: str) -> int:
        res = 0
        for i in range(len(s)):
            res += self.countPali(s, i, i)
            res += self.countPali(s, i, i + 1)
        return res
    def countPali(self, s, l, r):
        res = 0
        while l >= 0 and r < len(s) and s[l] == s[r]:
            res += 1
            l -= 1
            r += 1
        return res


# center expansion
class Solution:
    def countSubstrings(self, s: str) -> int:
        n = len(s)
        ans = 0
        for i in range(2 * n - 1):
            l, r = i // 2, (i + 1) // 2
            while l >= 0 and r < n and s[l] == s[r]:
                ans += 1
                l -= 1
                r += 1
        return ans


# dp
class Solution:
    def countSubstrings(self, s: str) -> int:
        n, res = len(s), 0
        dp = [[False] * n for _ in range(n)]
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                if s[i] == s[j] and (j - i <= 2 or dp[i + 1][j - 1]):
                    dp[i][j] = True
                    res += 1
        return res
```



### 300. 最长递增子序列
`Array` `Dynamic Programming` `Binary Search` \
Use DP or binary search with a tails array to track the smallest tail of increasing subsequences.

```python


```
















### 22. 括号生成
`String` `Backtracking` \
Backtrack by adding '(' when available and ')' when valid to build well-formed sequences.

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
`String` `Backtracking` `Mapping` \
Map digits to letter groups and backtrack over choices at each position.

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
`String` `Backtracking` `Validation` \
Backtrack through four segments, pruning invalid octets and leading zeros early.

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
`Array` `Greedy` `Two Pointers` \
Scan from the end to find the first decrease, swap with the next larger value, then reverse the suffix.

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
`Backtracking` `DFS` \
Use visited tracking to explore each unused number and collect full-length permutations.

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
`Backtracking` `DFS` \
Sort and skip duplicates by checking previous elements to avoid repeating permutations.

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
`Backtracking` `DFS` `Combinatorics` \
DFS from each start value to gather k-number combinations using pruning when size reaches k.

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
`Backtracking` `DFS` \
Recurse by choosing to include or skip each element, collecting every subset along the way.

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
`Backtracking` `DFS` \
Reuse candidates recursively while tracking the remaining sum to build valid combinations.

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
`Backtracking` `DFS` `Dedup` \
Sort candidates and skip duplicates during DFS to avoid repeated combination sets.

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
`Backtracking` `DFS` `Combinatorics` \
Choose k distinct digits from 1..9 via constrained DFS so their sum equals n.

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
`Math` `Backtracking` `DFS` \
Try divisors up to sqrt(n) and recurse with the quotient to collect factor combinations.

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
`Math` `Permutation` `Factorial Number` \
Use factorial numbering to select digits one-by-one for the k-th permutation.

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
`Backtracking` `String` `DFS` \
Toggle letter cases recursively whenever a letter is encountered to build all variants.

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

### 267. 回文排列 II
`Backtracking` `DFS` `Palindrome` \
Build palindromic halves by using characters in pairs and inserting the odd center when needed.

```python
!!!
class Solution:
    def generatePalindromes(self, s: str) -> List[str]:
        ct = Counter(s)
        odd = [k for k, v in ct.items() if v % 2]
        if len(odd) > 1: return []
        mid = odd[0] if odd else ""
        half = [k for k, v in ct.items() for _ in range(v // 2)]
        res = []
        vis = [False] * len(half)
        def dfs(cur):
            if len(cur) == len(half):
                res.append("".join(cur) + mid + "".join(cur[::-1]))
                return
            for i in range(len(half)):
                if vis[i] or (i > 0 and half[i] == half[i-1] and not vis[i-1]): 
                    continue
                vis[i] = True
                cur.append(half[i])
                dfs(cur)
                cur.pop()
                vis[i] = False
        dfs([])
        return res

class Solution:
    def generatePalindromes(self, s: str) -> List[str]:
        ct = Counter(s)
        odd = [k for k, v in ct.items() if v % 2]
        if len(odd) > 1: return []
        mid = odd[0] if odd else ""
        half = [k for k, v in ct.items() for _ in range(v // 2)]
        res = []
        def dfs(l):
            if l == len(half): res.append("".join(half) + mid + "".join(half[::-1])); return
            seen = set()
            for i in range(l, len(half)):
                if half[i] in seen: continue
                seen.add(half[i])
                half[l], half[i] = half[i], half[l]
                dfs(l + 1)
                half[l], half[i] = half[i], half[l]
        dfs(0)
        return res

class Solution:
    def generatePalindromes(self, s: str) -> List[str]:
        ct = Counter(s)
        odd = 0
        for v in ct.values():
            odd += v % 2
        if odd > 1:
            return []
        
        ctl = [k for k, v in ct.items() for _ in range(v // 2)]
        mid = ""
        for k, v in ct.items():
            if v % 2 == 1:
                mid = k
        
        res = []
        def dfs(cur, remaining):
            if len(cur) == len(ctl):
                res.append("".join(cur) + mid + "".join(cur[::-1]))
                return
            for i in range(len(remaining)):
                if i > 0 and remaining[i] == remaining[i-1]:
                    continue
                cur.append(remaining[i])
                dfs(cur, remaining[:i] + remaining[i+1:])
                cur.pop()
        dfs([], ctl)
        return res

class Solution:
    def generatePalindromes(self, s: str) -> list[str]:
        cnt = Counter(s)
        mid = ''
        target_len = len(s)
        for char, v in cnt.items():
            if v % 2 == 1:
                if mid: return []# More than one odd frequency char
                mid = char
                cnt[char] -= 1 # Use one for the center
        ans = []
        def dfs(path_str):
            if len(path_str) == target_len:
                ans.append(path_str)
                return
            for char in cnt:
                if cnt[char] >= 2:
                    cnt[char] -= 2      # Use two occurrences (one for each side)
                    dfs(char + path_str + char)
                    cnt[char] += 2      # Backtrack: restore the count
        dfs(mid)
        return ans

#fix
class Solution:
    def generatePalindromes(self, s: str) -> List[str]:
        ct = Counter(s)
        odd = 0
        for v in ct.values():
            odd += v % 2
        if odd > 1:
            return []
        ctl = [k for k, v in ct.items() for _ in range(v // 2)]
        mid = ""
        for k, v in ct.items():
            if v % 2 == 1:
                mid = k
        res = []
        def dfs(start, cur):
            if len(cur) == len(ctl):
                res.append("".join(cur) + mid + "".join(cur[::-1]))
                return
            for i in range(start, len(ctl)):
                if i > start and ctl[i] == ctl[i-1]:
                    continue
                cur.append(ctl[i])
                dfs(i, cur)
                cur.pop()
        dfs(0, [])
        return res
```



### 54. 螺旋矩阵
`Array` `Matrix` `Simulation` \
Simulate spiral traversal by marking visited cells and switching direction when needed.

```python
# visited or short path
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
`Array` `Matrix` `Simulation` \
Fill an n×n matrix in spiral order by rotating through four directions as you assign consecutive values.

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
`Linked List` `Matrix` `Simulation` \
Stream nodes into a spiral matrix, rotating directions and stopping when the list runs out.

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
`Array` `Two Pointers` `In-Place` \
Partition colors by swapping zeros to the left and twos to the right in a single pass.

```python
class Solution:
    def sortColors(self, nums: List[int]) -> None:
        nxt0, cur, nxt2 = 0, 0, len(nums) - 1
        while cur <= nxt2:
            if nums[cur] == 0:
                nums[nxt0], nums[cur] = nums[cur], nums[nxt0]
                nxt0 += 1
                cur += 1
            elif nums[cur] == 2:
                nums[nxt2], nums[cur] = nums[cur], nums[nxt2]
                nxt2 -= 1
            else:
                cur += 1

        # Time: O(n), Space: O(1)
```



### 249. 移位字符串分组
`String` `Hash Table` `Grouping` \
Normalize cyclic differences between adjacent letters to group shifted strings.

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
`Matrix` `Backtracking` `DFS` \
DFS through the board, marking visited cells to trace the input word sequentially.

```python
class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        def check(r, c, idx):
            if idx == len(word):
                return True
            if (r < 0 or r >= row or c < 0 or c >= col or 
                board[r][c] != word[idx]):
                    return False
            temp = board[r][c]
            board[r][c] = '#'
            res = check(r + 1, c, idx + 1) or check(r - 1, c, idx + 1) or check(r, c + 1, idx + 1) or check(r, c - 1, idx + 1)
            board[r][c] = temp
            return res

        row, col = len(board), len(board[0])
        for i in range(row):
            for j in range(col):
                if check(i, j, 0):
                    return True
        return False
```

### 212. 单词搜索 II
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None
    def insert(self, word):
        node = self
        for char in word:
            if char not in node.children: node.children[char] = TrieNode()
            node = node.children[char]
        node.word = word
class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        root = TrieNode()
        for w in words: root.insert(w)
        m, n, res = len(board), len(board),
        def dfs(r, c, parent):
            char = board[r][c]
            curr = parent.children[char]
            if curr.word:
                res.append(curr.word)
                curr.word = None
            board[r][c] = "#"
            for nr, nc in [(r+c), (r-c), (r, c+), (r, c-)]:
                if 0 <= nr < m and 0 <= nc < n and board[nr][nc] in curr.children:
                    dfs(nr, nc, curr)
            board[r][c] = char
            if not curr.children: parent.children.pop(char)
        for i in range(m):
            for j in range(n):
                if board[i][j] in root.children: dfs(i, j, root)
        return res

class Trie:
    def __init__(self):
        self.children = defaultdict(Trie)
        self.word = ""
    def insert(self, word):
        cur = self
        for c in word:
            cur = cur.children[c]
        cur.is_word = True
        cur.word = word


class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        trie = Trie()
        for word in words:
            trie.insert(word)
        def dfs(now, i1, j1):
            if board[i1][j1] not in now.children:
                return
            ch = board[i1][j1]
            now = now.children[ch]
            if now.word != "":
                ans.add(now.word)
            board[i1][j1] = "#"
            for i2, j2 in [(i1 + 1, j1), (i1 - 1, j1), (i1, j1 + 1), (i1, j1 - 1)]:
                if 0 <= i2 < m and 0 <= j2 < n:
                    dfs(now, i2, j2)
            board[i1][j1] = ch
        ans = set()
        m, n = len(board), len(board[0])
        for i in range(m):
            for j in range(n):
                dfs(trie, i, j)
        return list(ans)
```

### 88. 合并两个有序数组
`Array` `Two Pointers` `In-Place` \
Merge from the back so the larger elements shift right without overwriting unprocessed values.

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
`Array` `Two Pointers` `Math` \
Square values from both ends and fill the output backwards to keep results sorted.

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
`Array` `Two Pointers` `Math` \
Apply two pointers to place transformed values in order, handling parabolas opening up/down separately.

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
### 146. LRU 缓存
```python
# 1 sentinel
class Node:
    # 提高访问属性的速度，并节省内存
    __slots__ = 'prev', 'next', 'key', 'value'

    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value

class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.dummy = Node()
        self.dummy.prev = self.dummy
        self.dummy.next = self.dummy
        self.nodes = {}

    def get_node(self, key):
        if key not in self.nodes:
            return None
        node = self.nodes[key]
        self.remove(node)
        self.push_front(node)
        return node

    def get(self, key: int) -> int:
        node = self.get_node(key)
        return node.value if node else -1
        
    def put(self, key: int, value: int) -> None:
        node = self.get_node(key)
        if node:
            node.value = value
            return
        self.nodes[key] = node = Node(key, value)
        self.push_front(node)
        if len(self.nodes) > self.capacity:
            back_node = self.dummy.prev
            del self.nodes[back_node.key]
            self.remove(back_node)
        
    def remove(self, x):
        x.prev.next = x.next
        x.next.prev = x.prev
    
    def push_front(self, x):
        x.prev = self.dummy
        x.next = self.dummy.next
        x.prev.next = x
        x.next.prev = x

# head, tail
class LRUCache:
    def __init__(self, capacity: int):
        self.cache = dict()
        self.head = DLinkedNode()
        self.tail = DLinkedNode()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.capacity = capacity
        self.size = 0

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self.moveToHead(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key not in self.cache:
            node = DLinkedNode(key, value)
            self.cache[key] = node
            self.addToHead(node)
            self.size += 1
            if self.size > self.capacity:
                removed = self.removeTail()
                self.cache.pop(removed.key)
                self.size -= 1
        else:
            node = self.cache[key]
            node.value = value
            self.moveToHead(node)
    
    def addToHead(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def removeNode(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def moveToHead(self, node):
        self.removeNode(node)
        self.addToHead(node)

    def removeTail(self):
        node = self.tail.prev
        self.removeNode(node)
        return node
```

### 460. LFU Cache
```python
class Node:
    # 提高访问属性的速度，并节省内存
    __slots__ = 'prev', 'next', 'key', 'value', 'freq'

    def __init__(self, key=0, val=0):
        self.key = key
        self.value = val
        self.freq = 1  #  新书只读了一次

class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.key_to_node = {}
        def new_list() -> Node:
            dummy = Node()  # 哨兵节点
            dummy.prev = dummy
            dummy.next = dummy
            return dummy
        self.freq_to_dummy = defaultdict(new_list)

    def get_node(self, key: int) -> Optional[Node]:
        if key not in self.key_to_node:  # 没有这本书
            return None
        node = self.key_to_node[key]  # 有这本书
        self.remove(node)  # 把这本书抽出来
        dummy = self.freq_to_dummy[node.freq]
        if dummy.prev == dummy:  # 抽出来后，这摞书是空的
            del self.freq_to_dummy[node.freq]  # 移除空链表
            if self.min_freq == node.freq:  # 这摞书是最左边的
                self.min_freq += 1
        node.freq += 1  # 看书次数 +1
        self.push_front(self.freq_to_dummy[node.freq], node)  # 放在右边这摞书的最上面
        return node

    def get(self, key: int) -> int:
        node = self.get_node(key)
        return node.value if node else -1

    def put(self, key: int, value: int) -> None:
        node = self.get_node(key)
        if node:  # 有这本书
            node.value = value  # 更新 value
            return
        if len(self.key_to_node) == self.capacity:  # 书太多了
            dummy = self.freq_to_dummy[self.min_freq]
            back_node = dummy.prev  # 最左边那摞书的最下面的书
            del self.key_to_node[back_node.key]
            self.remove(back_node)  # 移除
            if dummy.prev == dummy:  # 这摞书是空的
                del self.freq_to_dummy[self.min_freq]  # 移除空链表
        self.key_to_node[key] = node = Node(key, value)  # 新书
        self.push_front(self.freq_to_dummy[1], node)  # 放在「看过 1 次」的最上面
        self.min_freq = 1

    def remove(self, x: Node) -> None:
        x.prev.next = x.next
        x.next.prev = x.prev

    def push_front(self, dummy: Node, x: Node) -> None:
        x.prev = dummy
        x.next = dummy.next
        x.prev.next = x
        x.next.prev = x

# ordereddict
# 为方便读者理解核心逻辑，该写法没有删除空字典，删除空字典的写法见【Python 写法二】
class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.key_to_value_and_freq = {}  # key -> [value, freq]
        # from collections import OrderedDict
        # OrderedDict = dict + 双向链表
        self.freq_to_dict = defaultdict(OrderedDict)  # freq -> OrderedDict（只保存 key）

    def get_list(self, key: int) -> Optional[List[int]]:
        lst = self.key_to_value_and_freq.get(key, None)
        if not lst:  # 没有这本书
            return None
        freq = lst[1]  # 获取这本书在第几摞
        del self.freq_to_dict[freq][key]  # 把这本书抽出来
        if not self.freq_to_dict[self.min_freq]:  # 最左边那摞书是空的
            self.min_freq += 1
        lst[1] += 1  # 看书次数 +1
        self.freq_to_dict[freq + 1][key] = None
        self.freq_to_dict[freq + 1].move_to_end(key, last=False)  # 放在右边这摞书的最上面
        return lst

    def get(self, key: int) -> int:
        lst = self.get_list(key)
        return lst[0] if lst else -1

    def put(self, key: int, value: int) -> None:
        lst = self.get_list(key)
        if lst:  # 有这本书
            lst[0] = value  # 更新 value
            return
        if len(self.key_to_value_and_freq) == self.capacity:  # 书太多了
            # 移除最左边那摞书的最下面的书
            k, _ = self.freq_to_dict[self.min_freq].popitem()
            del self.key_to_value_and_freq[k]
        self.key_to_value_and_freq[key] = [value, 1]  # 新书
        self.freq_to_dict[1][key] = None
        self.freq_to_dict[1].move_to_end(key, last=False)  # 放在「看过 1 次」的最上面
        self.min_freq = 1

# head, tail
class Node:
    def __init__(self, key, val, pre=None, nex=None, freq=0):
        self.pre = pre
        self.nex = nex
        self.freq = freq
        self.val = val
        self.key = key
        
    def insert(self, nex):
        nex.pre = self
        nex.nex = self.nex
        self.nex.pre = nex
        self.nex = nex
    
def create_linked_list():
    head = Node(0, 0)
    tail = Node(0, 0)
    head.nex = tail
    tail.pre = head
    return (head, tail)

class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.size = 0
        self.minFreq = 0
        self.freqMap = collections.defaultdict(create_linked_list)
        self.keyMap = {}

    def delete(self, node):
        if node.pre:
            node.pre.nex = node.nex
            node.nex.pre = node.pre
            if node.pre is self.freqMap[node.freq][0] and node.nex is self.freqMap[node.freq][-1]:
                self.freqMap.pop(node.freq)
        return node.key
        
    def increase(self, node):
        node.freq += 1
        self.delete(node)
        self.freqMap[node.freq][-1].pre.insert(node)
        if node.freq == 1:
            self.minFreq = 1
        elif self.minFreq == node.freq - 1:
            head, tail = self.freqMap[node.freq - 1]
            if head.nex is tail:
                self.minFreq = node.freq

    def get(self, key: int) -> int:
        if key in self.keyMap:
            self.increase(self.keyMap[key])
            return self.keyMap[key].val
        return -1

    def put(self, key: int, value: int) -> None:
        if self.capacity != 0:
            if key in self.keyMap:
                node = self.keyMap[key]
                node.val = value
            else:
                node = Node(key, value)
                self.keyMap[key] = node
                self.size += 1
            if self.size > self.capacity:
                self.size -= 1
                deleted = self.delete(self.freqMap[self.minFreq][0].nex)
                self.keyMap.pop(deleted)
            self.increase(node)
```

### 1756. Design Most Recently Used Queue
`Design` `Queue` `Hash Table` \
Use a list to maintain order and a set for quick membership checks; update on each fetch.
```python
```

### 297. 二叉树的序列化与反序列化
`Tree` `DFS` `BFS` \
Serialize with pre-order traversal including nulls; deserialize by reconstructing the tree from the list.
```python
class Codec:
    def serialize(self, root: TreeNode) -> str: 
        res = []
        def dfs(node):
            if not node:
                res.append("null")
                return
            res.append(str(node.val))
            dfs(node.left)
            dfs(node.right)
        dfs(root)
        return ','.join(res)

    def deserialize(self, data: str) -> TreeNode:
        vals = data.split(',')
        def dfs():
            if not vals:
                return None
            val = vals.pop(0)
            if val == "null":
                return None
            node = TreeNode(int(val))
            node.left = dfs()
            node.right = dfs()
            return node
        return dfs()
```

### 428. 序列化和反序列化 N 叉树
`Tree` `DFS` `BFS` \
Serialize by recording node values and child counts; deserialize by reconstructing the tree using these counts.
```python

class Node:
    def __init__(self, val=None, children=None):
        self.val = val
        self.children = children if children is not None else []

class Codec:
    def serialize(self, root: 'Node') -> str:
        res = []
        def dfs(node):
            if not node:
                return
            res.append(str(node.val))
            res.append(str(len(node.children)))
            for child in node.children:
                dfs(child)
        dfs(root)
        return ' '.join(res)

    def deserialize(self, data: str) -> 'Node':
        if not data:
            return None
        vals = data.split()
        def dfs():
            if not vals:
                return None
            val = int(vals.pop(0))
            count = int(vals.pop(0))
            node = Node(val)
            node.children = [dfs() for _ in range(count)]
            return node
        return dfs()
```

### 449. 序列化和反序列化二叉搜索树
`Tree` `DFS` `BST` \
Serialize with pre-order traversal; deserialize by inserting values into the BST.
```python
class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        res = []
        def dfs(node):
            if not node:
                return
            res.append(str(node.val))
            dfs(node.left)
            dfs(node.right)
        dfs(root)
        return ','.join(res)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        vals = data.split(',')
        def dfs():
            if not vals:
                return None
            val = int(vals.pop(0))
            node = TreeNode(val)
            node.left = dfs()
            node.right = dfs()
            return node
        return dfs()
```


### 56. 合并区间
`Array` `Intervals` `Sorting` \
Sort intervals by start and merge overlaps by extending the end when necessary.

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

### 57. 插入区间
`Array` `Intervals` `Sorting` \
Insert and merge intervals by adding non-overlapping ones directly and merging overlaps.

```python
class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        res = []
        start, end = newInterval
        i, n = 0, len(intervals)
        while i < n and intervals[i][1] < start:
            res.append(intervals[i])
            i += 1
        while i < n and intervals[i][0] <= end: 
            start = min(start, intervals[i][0])
            end = max(end, intervals[i][1])
            i += 1
        res.append([start, end])
        while i < n:
            res.append(intervals[i])
            i += 1
        return res
```

### 435. 无重叠区间
`Array` `Sorting` `Intervals` \ 
Sort intervals by end time and greedily select non-overlapping intervals to maximize count.
```python
# sort by start
class Solution:
    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:
        intervals.sort()
        res = 0
        preEnd = intervals[0][1]
        for start, end in intervals[1:]:
            if start >= preEnd:
                preEnd = end
            else:
                res += 1
                preEnd = min(end, preEnd)
        return res

# sort by end
class Solution:
    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:
        intervals.sort(key=lambda x: x[1])
        res = 0
        preEnd = intervals[0][1]
        for i in range(1, len(intervals)):
            if intervals[i][0] < preEnd:
                res += 1
                preEnd = min(preEnd, intervals[i][1])
            else:
                preEnd = intervals[i][1]
        return res
```

### 252. 会议室
`Array` `Sorting` `Intervals` \
Sort intervals by start and check for overlaps.

```python
class Solution:
    def canAttendMeetings(self, intervals: List[List[int]]) -> bool:
        intervals.sort()
        for i in range(1, len(intervals)):
            if intervals[i][0] < intervals[i-1][1]:
                return False
        return True
```

### 253. 会议室 II
`Array` `Sorting` `Heap` `Priority Queue` `Intervals` \
Sort intervals by start and use a min-heap to track end times for room allocation.

```python
# if overlap, +1 room

# pop and push
class Solution:
    def minMeetingRooms(self, intervals: List[List[int]]) -> int:
        intervals.sort()
        heap = []
        for itv in intervals:
            if heap and heap[0] <= itv[0]:
                heapq.heappop(heap)
            heapq.heappush(heap, itv[1])
        return len(heap)

# replace or push
class Solution:
    def minMeetingRooms(self, intervals: List[List[int]]) -> int:
        intervals.sort()
        rooms = [intervals[0][0]]   # 房间内保存最早结束时间
        for s, e in intervals:
            if rooms[0] <= s:       # 有空余房间
                heapq.heapreplace(rooms, e)
            else:                   # 没有空余房间
                heapq.heappush(rooms, e)
        return len(rooms) 
```

### 986. 区间列表的交集
`Array` `Two Pointers` `Intervals` \
Find intersections by advancing pointers based on interval ends and recording overlaps.
```python
class Solution:
    def intervalIntersection(self, firstList: List[List[int]], secondList: List[List[int]]) -> List[List[int]]:
        i = j = 0
        res = []
        while i < len(firstList) and j < len(secondList):
            start = max(firstList[i][0], secondList[j][0])
            end = min(firstList[i][1], secondList[j][1])

            if start <= end:
                res.append([start, end])
            
            if firstList[i][1] < secondList[j][1]:
                i += 1
            else:
                j += 1
        return res
```        

2848. 与车相交的点
`Geometry` `Math` `Intervals` \
Calculate intersection points of a line segment with a circle using geometric formulas.
```python
# diff arr
class Solution:
    def numberOfPoints(self, nums: List[List[int]]) -> int:
        C = max(y for _, y in nums)
        diff = [0] * (C + 2)
        for x, y in nums:
            diff[x] += 1
            diff[y + 1] -= 1
        
        ans = count = 0
        for i in range(1, C + 1):
            count += diff[i]
            if count > 0:
                ans += 1
        return ans

class Solution:
    def numberOfPoints(self, nums: List[List[int]]) -> int:
        C = max(y for _, y in nums)
        count = [0] * (C + 1)
        for x, y in nums:
            for i in range(x, y + 1):
                count[i] += 1
        
        ans = sum(1 for i in range(1, C + 1) if count[i] > 0)
        return ans
```

### 295. 数据流的中位数
`Heap` `Design` `Data Stream` \
Maintain two heaps to balance lower and upper halves of the data stream for median retrieval.
```python
class MedianFinder:
    def __init__(self):
        # small is a max-heap (invert values), large is a min-heap
        self.small = [] 
        self.large = []
    def addNum(self, num: int) -> None:
        heapq.heappush(self.small, -num)
        heapq.heappush(self.large, -heapq.heappop(self.small))
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))
    def findMedian(self) -> float:
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0])/2

class MedianFinder:
    def __init__(self):
        self.left = []  # 最大堆
        self.right = []  # 最小堆
    def addNum(self, num: int) -> None:
        if len(self.left) == len(self.right):
            heappush_max(self.left, heappushpop(self.right, num))
        else:
            heappush(self.right, heappushpop_max(self.left, num))
    def findMedian(self) -> float:
        if len(self.left) > len(self.right):
            return self.left[0]
        return (self.left[0] + self.right[0]) / 2
```

### 480. 滑动窗口中位数
`Heap` `Sliding Window` `Data Stream` \
Maintain two heaps for the sliding window and use a lazy deletion strategy to handle removals.
```python

```

1094. 拼车
1109. 航班预订统计
2381. 字母移位 II
2406. 将区间分为最少组数
2772. 使数组中的所有元素都等于零
2528. 最大化城市的最小供电站数目

3355. 零数组变换 I

### 55. 跳跃游戏
`Array` `Greedy` `Dynamic Programming` \
Greedily track the farthest reachable index to determine if the end is reachable.
```python
class Solution:
    def canJump(self, nums: List[int]) -> bool:
        mx = 0
        for i, jump in enumerate(nums):
            if i > mx:  # 无法到达 i
                return False
            mx = max(mx, i + jump)  # 从 i 最右可以跳到 i+jump
        return True

def canJump(nums: List[int]) -> bool:
    n = len(nums)
    dp = [False] * n
    dp[0] = True  # The start is always reachable
    for i in range(n):
        if not dp[i]:
            continue
        furthest_jump = min(i + nums[i], n - 1)
        for j in range(i + 1, furthest_jump + 1):
            dp[j] = True
            if j == n - 1:
                return True
    return dp[n-1]

# Bottom-up O(n^2)
class Solution:
    def canJump(self, nums: List[int]) -> bool:
        n = len(nums)
        dp = [False] * n
        dp[n-1] = True
        for i in range(n - 2, -1, -1):
            furthest_jump = min(i + nums[i], n - 1)
            for j in range(i + 1, furthest_jump + 1):
                if dp[j]:
                    dp[i] = True
                    break
        return dp[0]

# Top-down O(n^2)
class Solution:
    def canJump(self, nums: List[int]) -> bool:
        memo = {}
        def dfs(i):
            if i in memo:
                return memo[i]
            if i == len(nums) - 1:
                return True
            if nums[i] == 0:
                return False
            end = min(len(nums), i + nums[i] + 1)
            for j in range(i + 1, end):
                if dfs(j):
                    memo[i] = True
                    return True
            memo[i] = False
            return False
        return dfs(0)

# O(n!)
class Solution:
    def canJump(self, nums: List[int]) -> bool:
        def dfs(i):
            if i == len(nums) - 1:
                return True
            end = min(len(nums) - 1, i + nums[i])
            for j in range(i + 1, end + 1):
                if dfs(j):
                    return True
            return False
        return dfs(0)


```

### 70. 爬楼梯
`Dynamic Programming` `Math` \
用斐波那契思路统计不重复的上楼方法。
```python
class Solution:
    def climbStairs(self, n: int) -> int:
        if n <= 2: return n
        dp = [0] * (n + 1)
        dp[1] = 1
        dp[2] = 2
        for i in range(3, n + 1):
            dp[i] = dp[i-1] + dp[i-2]
        return dp[n]

class Solution:
    def climbStairs(self, n: int) -> int:
        cache = [-1] * n
        def dfs(i):
            if i >= n:
                return i == n
            if cache[i] != -1:
                return cache[i]
            cache[i] = dfs(i + 1) + dfs(i + 2)
            return cache[i]
        return dfs(0)

class Solution:
    def climbStairs(self, n: int) -> int:
        one, two = 1, 1
        for i in range(n - 1):
            temp = one
            one = one + two
            two = temp
        return one

class Solution:
    def climbStairs(self, n: int) -> int:
        def dfs(i):
            if i >= n:
                return i == n
            return dfs(i + 1) + dfs(i + 2)
        return dfs(0)
```

### 198. 打家劫舍
`Dynamic Programming` `Greedy` \
在不触发警报的前提下选择不相邻房屋以最大化收益。
```python
# init manual first 2, to get it rolling
class Solution:
    def rob(self, nums: List[int]) -> int:
        if len(nums) == 1: return nums[0]
        dp = [0] * len(nums)
        dp[0] = nums[0]
        dp[1] = max(nums[0], nums[1])
        for i in range(2, len(nums)):
            dp[i] = max(dp[i-1], dp[i-2] + nums[i])
        return dp[-1]

# init with extra 2
class Solution:
    def rob(self, nums: List[int]) -> int:
        f = [0] * (len(nums) + 2)
        for i, x in enumerate(nums):
            f[i + 2] = max(f[i + 1], f[i] + x)
        return f[-1]

class Solution:
    def rob(self, nums: List[int]) -> int:
        # dfs(i) 表示从 nums[0] 到 nums[i] 最多能偷多少
        @cache  # 缓存装饰器，避免重复计算 dfs 的结果
        def dfs(i: int) -> int:
            if i < 0:  # 递归边界（没有房子）
                return 0
            return max(dfs(i - 1), dfs(i - 2) + nums[i])

        return dfs(len(nums) - 1)  # 从最后一个房子开始思考

class Solution:
    def rob(self, nums: List[int]) -> int:
        f0 = f1 = 0
        for x in nums:
            f0, f1 = f1, max(f1, f0 + x)
        return f1

class Solution:
    def rob(self, nums: list[int]) -> int:
        rob1, rob2 = 0, 0
        # [rob1, rob2, n, n+1, ...]
        for n in nums:
            temp = max(n + rob1, rob2)
            rob1 = rob2
            rob2 = temp
        return rob2

```

### 213. 打家劫舍 II
`Dynamic Programming` `Greedy` `Circular` \
环形房屋经由拆成两段线性区间（去掉首或尾）完成 DP。
```python
class Solution:
    def rob(self, nums: List[int]) -> int:
        def rob1(nums):
            pre, cur  = 0, 0
            for n in nums:
                pre, cur = cur, max(pre + n, cur)
            return cur
        return max(rob1(nums[:-1]), rob1(nums[1:])) if len(nums) != 1 else nums[0]

class Solution:
    def rob(self, nums: List[int]) -> int:
        n = len(nums)
        if n == 1: return nums[0]
        def rob_linear(h_list: List[int]) -> int:
            m = len(h_list)
            if m == 0: return 0
            dp = [0] * m
            dp[0] = h_list[0]
            if m > 1:
                dp[1] = max(h_list[0], h_list[1])
            for i in range(2, m):
                dp[i] = max(dp[i-1], h_list[i] + dp[i-2])
            return dp[-1]
        return max(rob_linear(nums[1:]), rob_linear(nums[:-1]))
```

### 337. 打家劫舍 III
`Tree` `DFS` `Dynamic Programming` \
Use DFS to decide whether to rob the current node or its children for maximum gain.
```python
# not_rob = max(rob, not_rob...)
class Solution:
    def rob(self, root: Optional[TreeNode]) -> int:
        def dfs(node):
            if not node:
                return 0, 0
            left_rob, left_not_rob = dfs(node.left)
            right_rob, right_not_rob = dfs(node.right)
            rob = left_not_rob + right_not_rob + node.val
            not_rob = max(left_rob, left_not_rob) + max(right_rob, right_not_rob)
            return rob, not_rob
        return max(dfs(root))
```



### 91. 解码方法
`Dynamic Programming` `Math` \
验证一位或两位组合是否合法并累加解密路径数。

```python

```

### 322. 零钱兑换
`Dynamic Programming` `Knapsack` \
把每种硬币视为完全背包，枚举金额更新最少硬币数。
```python
# dp, top-down, memo {}
class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        memo = {}
        def dfs(rem):
            if rem == 0: return 0
            if rem in memo: return memo[rem]
            res = float('inf')
            for coin in coins:
                if rem - coin >= 0:
                    # Recursive call now returns an actual number
                    res = min(res, 1 + dfs(rem - coin))
            memo[rem] = res
            return res # FIX: Return the calculated value
        ans = dfs(amount)
        return ans if ans != float('inf') else -1

@cache
def dfs(rem):

# dp
class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        dp = [amount + 1] * (amount + 1)
        dp[0] = 0

        for a in range(1, amount + 1):
            for c in coins:
                if a - c >= 0:
                    dp[a] = min(dp[a], 1 + dp[a - c])
        return dp[amount] if dp[amount] != amount + 1 else -1

# bfs
class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        if amount == 0:
            return 0
        q = deque([0])
        seen = [False] * (amount + 1)
        seen[0] = True
        res = 0
        while q:
            res += 1
            for _ in range(len(q)):
                cur = q.popleft()
                for coin in coins:
                    nxt = cur + coin
                    if nxt == amount:
                        return res
                    if nxt > amount or seen[nxt]:
                        continue
                    seen[nxt] = True
                    q.append(nxt)
        return -1


```


### 53. 最大子数组和
`Array` `Dynamic Programming` `Divide and Conquer` `Kadane's Algorithm` \
Use Kadane's algorithm to track current and global maximum subarray sums.

```python
# kadane's algorithm
# maintain cur and res
class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        curmax = 0
        res = -float('inf')
        for n in nums:
            curmax = max(curmax + n, n)
            res = max(res, curmax)
        return res

# dp[]
# max(dp[i-1] + n, n) -> max(dp)   potential negatives
class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        dp = [0] * len(nums)
        dp[0] = nums[0]
        for i in range(1, len(nums)):
            n = nums[i]
            dp[i] = max(dp[i-1] + n, n)
        return max(dp)
```


### 152. 乘积最大子数组
`Array` `Dynamic Programming` \
维护区间最大值/最小值，应对负数造成的翻转。

```python
# cur max/min
class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        res = -float('inf')
        cur_max, cur_min = 1, 1
        for n in nums:
            val1 = (cur_max * n, cur_min * n, n)
            val2 = (cur_max * n, cur_min * n, n)
            cur_max = max(val1)
            cur_min = min(val2)
            res = max(res, cur_max)
        return res

# dp
class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        n = len(nums)
        f_max = [0] * n
        f_min = [0] * n
        f_max[0] = f_min[0] = nums[0]
        for i in range(1, n):
            x = nums[i]
            f_max[i] = max(f_max[i - 1] * x, f_min[i - 1] * x, x)
            f_min[i] = min(f_max[i - 1] * x, f_min[i - 1] * x, x)
        return max(f_max)


class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        if not nums: return 0
        res = -float('inf')
        cur_min, cur_max = 1, 1
        for n in nums:
            if n < 0:
                cur_max, cur_min = cur_min, cur_max
            cur_max = max(n, n * cur_max)
            cur_min = min(n, n * cur_min)
            res = max(res, cur_max)
        return res
```

### 628. 三个数的最大乘积
`Array` \
Sort the array and consider the product of the top three numbers or the product of the two smallest (possibly negative) and the largest number.
```python
# case analysis
# all positive
# all negative
# 3 - n n p,    n p p
# 
class Solution:
    def maximumProduct(self, nums: List[int]) -> int:
        nums.sort()
        n = len(nums)
        return max(nums[0] * nums[1] * nums[n-1], 
                   nums[n-1] * nums[n-2] * nums[n-3])

class Solution:
    def maximumProduct(self, nums: list[int]) -> int:
        max3 = heapq.nlargest(3, nums)
        min2 = heapq.nsmallest(2, nums)
        return max(max3[0] * max3[1] * max3[2], 
                   min2[0] * min2[1] * max3[0])
```

### 238. 除了自身以外数组的乘积
`Array` `Dynamic Programming` \
Compute prefix and suffix products to get the product of all elements except the current one without using division
```python
class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        pre = [1] * n
        for i in range(1, n):
            pre[i] = pre[i - 1] * nums[i - 1]

        suf = [1] * n
        for i in range(n - 2, -1, -1):
            suf[i] = suf[i + 1] * nums[i + 1]

        return [p * s for p, s in zip(pre, suf)]
```


### 139. 单词拆分
`Dynamic Programming` `String` \
dp 记录每个前缀是否可拆分，并据此延展后续状态。

```python

```

### 300. 最长递增子序列
`Dynamic Programming` `Binary Search` \
用 patience sort 或 dp/二分组合求出 LIS。

```python

```

### 256. 粉刷房子
`Dynamic Programming` `Matrix` \
Paint each house with the minimum cost considering the previous house's color choices.
```python
class Solution:
    def minCost(self, costs: List[List[int]]) -> int:
        if not costs: return 0
        r, b, g = 0, 0, 0
        for c_r, c_b, c_g in costs:
            r, b, g = c_r + min(b, g), c_b + min(r, g), c_g + min(r, b)
        return min(r, b, g)

class Solution:
    def minCost(self, costs: List[List[int]]) -> int:
        if len(costs) == 1: return min(costs[0])
        n = len(costs)
        dp = [[0, 0, 0] for _ in range(n)]
        dp[0] = costs[0]
        for i in range(1, n):
            dp[i][0] = min(dp[i-1][1], dp[i-1][2]) + costs[i][0]
            dp[i][1] = min(dp[i-1][0], dp[i-1][2]) + costs[i][1]
            dp[i][2] = min(dp[i-1][0], dp[i-1][1]) + costs[i][2]
        return min(dp[-1])
```

### 276. 栅栏涂色
`Dynamic Programming` `Math` \
Count ways to paint fences with constraints using DP or combinatorial formulas.
```python
# rolling vars
class Solution:
    def numWays(self, n: int, k: int) -> int:
        if n == 1: return k
        two_back = k
        one_back = k*k
        for i in range(3, n + 1):
            one_back, two_back = (k - 1) * (one_back + two_back), one_back
        return one_back

# bottom-up, dp[]]
class Solution:
    def numWays(self, n: int, k: int) -> int:
        if n == 1:
            return k
        if n == 2:
            return k * k
        total_ways = [0] * (n + 1)
        total_ways[1] = k
        total_ways[2] = k * k
        for i in range(3, n + 1):
            total_ways[i] = (k - 1) * (total_ways[i - 1] + total_ways[i - 2])
        return total_ways[n]

# top-down with lru_cache
class Solution:
   def numWays(self, n: int, k: int) -> int:
       @lru_cache(None)
       def total_ways(i):
           if i == 1: 
               return k
           if i == 2: 
               return k * k
           
           return (k - 1) * (total_ways(i - 1) + total_ways(i - 2))
       
       return total_ways(n)

```


### 740. 删除并获得点数
`Array` `Dynamic Programming` `Hash Table` \
Map values to their total points and apply house robber logic to maximize points.
```python
class Solution:
    def deleteAndEarn(self, nums: List[int]) -> int:
        store = [0] * (max(nums))
        for x in nums:
            store[x-1] += x
        f0 = f1 = 0
        for x in store:
            f0, f1 = f1, max(f1, f0 + x)
        return f1
```

### 2611. 老鼠和奶酪
`Greedy` `Sorting` `Array` \
Calculate the gain for each cheese and select the top k gains for the first mouse.
```python

```


### 400. 第 N 位数字
`Math` `String` \
Calculate the range of numbers for each digit length and find the target digit by indexing into the appropriate number.
```python

```

