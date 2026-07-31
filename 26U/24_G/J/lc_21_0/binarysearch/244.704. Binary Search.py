"""
244.704. Binary Search
二分查找

Given a sorted (in ascending order) integer array nums of n elements and a target 
value, write a function to search target in nums. If target exists, then return its index, otherwise return -1.


Example 1:

Input: nums = [-1,0,3,5,9,12], target = 9
Output: 4
Explanation: 9 exists in nums and its index is 4

Example 2:

Input: nums = [-1,0,3,5,9,12], target = 2
Output: -1
Explanation: 2 does not exist in nums so return -1
 

Note:

You may assume that all elements in nums are unique.
n will be in the range [1, 10000].
The value of each element in nums will be in the range [-9999, 9999].



"""

def search(self, nums, target):
    index = bisect.bisect_left(nums, target)
    return index if index < len(nums) and nums[index] == target else -1


def binarySearch (arr, l, r, x): 
    if r >= l: 
        mid = l + (r - l) // 2
        if arr[mid] == x: 
            return mid 
        elif arr[mid] > x: 
            return binarySearch(arr, l, mid-1, x) 
        else: 
            return binarySearch(arr, mid + 1, r, x) 
    else: 
        return -1


def binarySearch(arr, l, r, x): 
    while l <= r: 
        mid = l + (r - l) // 2
        if arr[mid] == x: 
            return mid 

        elif arr[mid] < x: 
            l = mid + 1
        else: 
            r = mid - 1 
    return -1




def search(self, nums, target):
	def recur_search(nums,target,left,right):
        if left <= right:
            mid = (left+right)//2
            if nums[mid] == target:
                return mid
            elif nums[mid] < target:
                return recur_search(nums,target,mid+1,right)
            else:
                return recur_search(nums,target,left,mid-1)
        else: return -1
    left,right = 0, len(nums)-1
    return recur_search(nums,target,left,right)







def search(self, nums, target):
    #corner case: nums is empty
    if not nums or len(nums) == 0:
        return -1
    left, right = 0, len(nums) - 1
    #corner case: target value is out of the list's value range
    if target < nums[left] or target > nums[right]:
        return -1

    #lock the target in left, right and mid three numbers.
    while left + 1 < right:     
        mid = left + (right - left) / 2
        if nums[mid] > target:
            right = mid
        elif nums[mid] < target:
            left = mid
        else:
            return mid    
    #if the target is not the mid, check the right and left
    if nums[right] == target:
        return right
    if nums[left] == target:
        return left
    return -1

















































































































































