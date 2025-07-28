"""
155.1464. Maximum Product of Two Elements in an Array


Given the array of integers nums, you will choose two different indices i and j of that 
array. Return the maximum value of (nums[i]-1)*(nums[j]-1).
 

Example 1:

Input: nums = [3,4,5,2]
Output: 12 
Explanation: If you choose the indices i=1 and j=2 (indexed from 0), you will get the 
maximum value, that is, (nums[1]-1)*(nums[2]-1) = (4-1)*(5-1) = 3*4 = 12. 
Example 2:

Input: nums = [1,5,4,5]
Output: 16
Explanation: Choosing the indices i=1 and j=3 (indexed from 0), you will get the maximum 
value of (5-1)*(5-1) = 16.
Example 3:

Input: nums = [3,7]
Output: 12
 

Constraints:

2 <= nums.length <= 500
1 <= nums[i] <= 10^3


"""




return (nums.pop(nums.index(max(nums)))-1)*(nums.pop(nums.index(max(nums)))-1)


*args, x, y = sorted(nums)
return (x - 1) * (y - 1)


def maxProduct(self, nums: List[int]) -> int:
    heap = nums[:2]
    heapq.heapify(heap)
    
    for i in range(2, len(nums)):
        if nums[i] > heap[0]:
            heapq.heappushpop(heap, nums[i])
            
    return  (heap[0] - 1) * (heap[1] - 1)



def maxProduct(self, nums: List[int]) -> int:
    m = n = -math.inf
    for num in nums:
        if num >= m:
            n = m
            m = num
        elif num > n:
            n = num
    return (m - 1) * (n - 1)


def maxProduct(self, nums):
    max_1 = max(nums)
    nums.remove(max_1)
    max_2 = max(nums)
    return (max_1-1)*(max_2-1)



def maxProduct(self, nums):
    first, second = 0, 0
    for number in nums:
        if number > first:
            # update first largest and second largest
            first, second = number, first 
        else:
            # update second largest
            second = max( number, second)
    return (first - 1) * (second - 1)


def maxProduct(self, nums: List[int]) -> int:
    n2 = nums
    i = nums.pop(nums.index(max(nums)))
    j = nums.pop(nums.index(max(nums)))
    return (i-1)*(j-1)


def maxProduct(self, nums):
    nums.sort()
    return (nums[-1] -1) * (nums[-2]-1)






































































