
704. 二分查找
class Solution:
	def search(self, nums: List[int], target: int) -> int:

	    n = len(nums)
	    left, right = 0, n - 1

	    while left <= right:
	        mid = (right - l) // 2 + l
	        if nums[mid] == target:
	            return mid
	        elif nums[mid] > target:
	            right = mid - 1
	        else:
	            left = mid + 1

	    return -1


mid = (right - left) // 2 + l

class Solution:
	def search(self, nums: List[int], target: int) -> int:
	    l, r = 0, len(nums)
	    while l < r:
	        m = (l + r) // 2
	        if nums[m] >= target:
	            r = m
	        else:
	            l = m + 1
	    if l < len(nums) and nums[l] == target:
	        return l
	    return -1


def bs(t, nums):
    l, r = 0, len(nums)
    while l < r:
        m = (l + r) // 2
        if t <= nums[m]:
            r = m
        else:
            l = m + 1
    return l



#Lower Bound with l <= r:
def bs(t, nums):
    l, r = 0, len(nums) - 1
    while l <= r:
        m = (l + r) // 2
        if t <= nums[m]:
            r = m - 1
        else:
            l = m + 1
    return l  # Need to adjust return value



# Upper Bound with r = len(nums) and l < r:
def bs(t, nums):
    l, r = 0, len(nums)
    while l < r:
        m = (l + r) // 2
        if t < nums[m]:
            r = m
        else:
            l = m + 1
    return l


# Upper Bound with l <= r:
def bs(t, nums):
    l, r = 0, len(nums) - 1
    while l <= r:
        m = (l + r) // 2
        if t < nums[m]:
            r = m - 1
        else:
            l = m + 1
    return l


# Exact Match with r = len(nums) and l < r
def bs(t, nums):
    l, r = 0, len(nums)
    while l < r:
        m = (l + r) // 2
        if t <= nums[m]:
            r = m
        else:
            l = m + 1
    if l < len(nums) and nums[l] == t:
        return l
    return -1


# Exact Match with l <= r:
def bs(t, nums):
    l, r = 0, len(nums) - 1
    while l <= r:
        m = (l + r) // 2
        if t == nums[m]:
            return m
        elif t < nums[m]:
            r = m - 1
        else:
            l = m + 1
    return -1


# Variation 4: Find Last Position Where nums[i] < t
# This finds the last position where nums[i] < t, which can be used to determine the insertion point as result + 1.
# Last < t with r = len(nums) and l < r:
def bs(t, nums):
    l, r = 0, len(nums)
    while l < r:
        m = (l + r) // 2
        if t <= nums[m]:
            r = m
        else:
            l = m + 1
    return l - 1  # Last position where nums[i] < t, or -1 if none


# Last < t with l <= r:
def bs(t, nums):
    l, r = 0, len(nums) - 1
    while l <= r:
        m = (l + r) // 2
        if t <= nums[m]:
            r = m - 1
        else:
            l = m + 1
    return r  # Last position where nums[i] < t, or -1 if none


# Variation 5: Iterative Search with Early Exit
# For an exact match, we can exit early when t is found:
def bs(t, nums):
    l, r = 0, len(nums)
    while l < r:
        m = (l + r) // 2
        if t == nums[m]:
            return m
        elif t < nums[m]:
            r = m
        else:
            l = m + 1
    return l  # Insertion point if not found



349. 两个数组的交集
1213. 三个有序数组的交集
2248. 多个数组求交集




2529. 正整数和负整数的最大计数
class Solution:
    def lowerBound(self, nums, val):
        l, r = 0, len(nums)
        while l < r:
            m = (l + r) // 2
            if nums[m] >= val:
                r = m
            else:
                l = m + 1
        return l

    def maximumCount(self, nums: List[int]) -> int:
        pos1 = self.lowerBound(nums, 0)
        pos2 = self.lowerBound(nums, 1)
        return max(pos1, len(nums) - pos2)






69. x 的平方根

class Solution:
    def mySqrt(self, x: int) -> int:
        l, r = 0, x
        res = 0
        while l <= r:
            mid = (l + r) // 2
            if mid * mid <= x:
                res = mid
                l = mid + 1
            else:
                r = mid - 1
        return res

	
	367. 有效的完全平方数
		class Solution:
		    def isPerfectSquare(self, num: int) -> bool:
		        l, r = 0, num - 1
		        while l <= r:
		            m = (l + r) // 2
		            sqr = m * m
		            if sqr == num:
		                return True
		            elif sqr < num:
		                l = m + 1
		            else:
		                r = m - 1
		        return False

35. 搜索插入位置
class Solution:
	def searchInsert(self, nums: List[int], target: int) -> int:
        n = len(nums)
        l, r = 0, n - 1
        res = n

        while l <= r:
            mid = (r - l) // 2 + l
            if target <= nums[mid]:
                res = mid
                r = mid - 1
            else:
                l = mid + 1
        
        return res

class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
	    l, r = 0, len(nums)
	    while l < r:
	        m = (l + r) // 2
	        if nums[m] >= target:
	            r = m
	        else:
	            l = m + 1
	    return r


	278. 第一个错误的版本
	class Solution:
	    def firstBadVersion(self, n: int) -> int:
	        l, r = 1, n
	        while l < r:
	            mid = (l + r) // 2
	            if isBadVersion(mid):
	                r = mid
	            else:
	                l = mid + 1
	        return l


	class Solution:
	    def firstBadVersion(self, n: int) -> int:
	        l, r = 1, n
	        while l <= r:
	            mid = (l + r) // 2
	            if isBadVersion(mid):
	                r = mid - 1
	            else:
	                l = mid + 1
	        return l

	374. 猜数字大小

	3065. 超过阈值的最少操作数 I





34. 在排序数组中查找元素的第一个和最后一个位置

import bisect

class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        return bisect_left(nums, target)






1351. 统计有序矩阵中的负数
class Solution:
    def countNegatives(self, grid: List[List[int]]) -> int:
        m, n = len(grid), len(grid[0])
    
        # Outer binary search: Find the first row where a negative number appears
        l, r = 0, m
        while l < r:
            mid = (l + r) // 2
            if grid[mid][n-1] >= 0:  # Last element of row is non-negative
                l = mid + 1
            else:  # Last element is negative, search earlier rows
                r = mid
        
        first_neg_row = l  # First row where grid[l][n-1] < 0
        if first_neg_row == 0:  # All rows may have negatives starting from row 0
            first_neg_row = 0
        elif first_neg_row == m:  # No negatives found
            return 0
        
        # Count negatives in rows from first_neg_row to m-1
        total = 0
        for i in range(first_neg_row, m):
            # Inner binary search: Find first negative in row i
            l, r = 0, n
            while l < r:
                mid = (l + r) // 2
                if grid[i][mid] >= 0:
                    l = mid + 1
                else:
                    r = mid
            first_neg_col = l  # First index where grid[i][l] < 0
            total += n - first_neg_col  # Count of negatives in row i
        
        return total




1. two sum
2824. 统计和小于目标的下标对数目


class Solution:
    def countPairs(self, nums: List[int], target: int) -> int:
        return sum(x + y < target for x, y in combinations(nums, 2))




class Solution:
    def countPairs(self, nums: List[int], target: int) -> int:
        nums.sort()
        return sum(bisect_left(nums, target - nums[i], 0, i) for i in range(1, len(nums)))


class Solution:
    def countPairs(self, nums: List[int], target: int) -> int:
        nums.sort()
        i, j = 0, len(nums) - 1
        res = 0
        while i < j:
            while i < j and nums[i] + nums[j] >= target:
                j -= 1
            res += j - i
            i += 1
        return res






2389. 和有限的最长子序列
!!
class Solution:
    def answerQueries(self, nums: List[int], queries: List[int]) -> List[int]:
        f = list(accumulate(sorted(nums)))
        return [bisect_right(f, q) for q in queries]


class Solution:
    def answerQueries(self, nums: List[int], queries: List[int]) -> List[int]:
        nums.sort()
        for i in range(1, len(nums)):
            nums[i] += nums[i - 1]  # 原地求前缀和
        for i, q in enumerate(queries):
            queries[i] = bisect_right(nums, q)  # 复用 queries 作为答案
        return queries



class Solution:
    def answerQueries(self, nums: List[int], queries: List[int]) -> List[int]:
        def bs(nums, t):
            l, r = 0, len(nums)
            while l < r:
                m = (l + r) // 2
                if t < nums[m]:
                    r = m
                else:
                    l = m + 1
            return l

        nums.sort()
        res = [0] * len(queries)
        for i in range(1, len(nums)):
            nums[i] += nums[i - 1]
        
        for i in range(len(queries)):
            q = queries[i]
            res[i] = bs(nums, q)

        return res


2824. 统计和小于目标的下标对数目
class Solution:
    def countPairs(self, nums: List[int], target: int) -> int:
        nums.sort()
        return sum(bisect_left(nums, target - nums[i], 0, i) for i in range(1, len(nums)))


class Solution:
    def countPairs(self, nums: List[int], target: int) -> int:
        return sum(x + y < target for x, y in combinations(nums, 2))





1385. 两个数组间的距离值
class Solution:
    def findTheDistanceValue(self, arr1: List[int], arr2: List[int], d: int) -> int:
        cnt = 0
        for x in arr1:
            if all(abs(x - y) > d for y in arr2):
                cnt += 1
        return cnt



class Solution:
    def findTheDistanceValue(self, arr1: List[int], arr2: List[int], d: int) -> int:
        def bs(t, nums):
            l, r = 0, len(nums)
            while l < r:
                m = (l + r) // 2
                if nums[m] > t:
                    r = m
                else:
                    l = m + 1
            return l
        
        arr2.sort()
        cnt = 0
        for x in arr1:
            p = bs(x, arr2)
            if p == len(arr2) or abs(x - arr2[p]) > d:
                if p == 0 or abs(x - arr2[p - 1]) > d:
                    cnt += 1
        return cnt








LCP 18. 早餐组合
class Solution:
    def breakfastNumber(self, staple: List[int], drinks: List[int], x: int) -> int:
        def bs(nums, t):
            l, r = 0, len(nums) - 1
            while l <= r:
                m = (l + r) // 2
                if t < nums[m]:
                    r = m - 1
                else:
                    l = m + 1
            return l

        res = 0
        drinks.sort()
        for s in staple:
            b = bs(drinks, x - s)
            res += b
        return res%(10**9+7)





1539. 第 k 个缺失的正整数
!!!


##########################################################################################
# mid


209. 长度最小的子数组




























