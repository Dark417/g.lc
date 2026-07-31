"""
747. Largest Number At Least Twice of Others
In a given integer array nums, there is always exactly one largest element.
Find whether the largest element in the array is at least twice as much as every other number in the array.
If it is, return the index of the largest element, otherwise return -1.

Example 1:
Input: nums = [3, 6, 1, 0]
Output: 1
Explanation: 6 is the largest integer, and for every other number in the array x,
6 is more than twice as big as x.  The index of value 6 is 1, so we return 1.
 

Example 2:
Input: nums = [1, 2, 3, 4]
Output: -1
Explanation: 4 isn't at least as big as twice the value of 3, so we return -1.

psd


"""

ipt = [1, 2, 5, 5]


#D
def largest_twice(nums):
    if len(nums) <= 1 :
        return False

    max0 = max(nums)
    nums2 = nums.remove(max0)
    max2 = max(nums2)

    return (True if max0 > 2*max2 else False)


res = max(ipt)
nums2 = ipt.remove(res)

print(nums2)
# print(ipt.index(res))

# res = largest_twice(ipt)
# print(res)




#sort
def dis_sort(nums):
    if len(nums) < 2:
        return 0
    sorted_nums = sorted(nums)
    largest_num = sorted_nums[-1]
    if sorted_nums[-2] * 2 <= largest_num:
        return nums.index(largest_num)
    else:
        return -1 


#
def dis_1(nums):
    m = float('-inf')
    index = -1
    
    for i,x in enumerate(nums):
        if x>=m:
            index = i if x>=2*m else -1
            m = x
        elif m<2*x:
            index = -1
            
    return index


#
def dis_2(nums):
    exist, max_ix, max_num = True, -1, float('-inf')
    
    for i, num in enumerate(nums):
        if num > max_num:
            exist = True if num >= 2 * max_num else False
            max_num = num
            max_ix = i
        elif num * 2 > max_num:
            exist = False
    
    return max_ix if exist else -1

#dis 3
def dis_3(nums):

    largest = nums[0]
    second_largest = -float('inf')
    largest_index = 0
    
    for idx in range(1,len(nums)):
        if nums[idx]>largest:
            second_largest = largest
            largest = nums[idx]
            largest_index = idx
        elif nums[idx]>second_largest:
            second_largest = nums[idx]
    return largest_index if largest >= second_largest*2 else -1

#dis n
# def dis_n(nums):

# 	max1 = 0
#     max2 = 0
#     for num in nums:
#         if num > max1:
#             max2 = max1
#             max1 = num
#         elif num > max2:
#             max2 = num
            
#     if max1 >= max2*2:
#         return nums.index(max1)
#     else:
#         return -1
	
	
	
	
	
	
