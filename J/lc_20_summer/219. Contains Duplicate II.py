"""
219. Contains Duplicate II
Given an array of integers and an integer k, find out whether there are two distinct indices i and j in the array such that nums[i] = nums[j] and the absolute difference between i and j is at most k.

Example 1:
Input: nums = [1,2,3,1], k = 3
Output: true
Example 2:

Input: nums = [1,0,1,1], k = 1
Output: true
Example 3:

Input: nums = [1,2,3,1,2,3], k = 2
Output: false

psd
for every interval
    for i in range(len(nums) - k)
check if duplicate
    hash


"""
nums = [1,2,3,1,2,3]
# nums = [99, 99]
k = 3
# print(len(nums))


# def if_duplicate(nums, k):
#     hash = {}
#     s = 0
#
#     if len(nums) < 2:
#         return False
#
#     if len(nums) == 2:
#         if nums[0] == nums[1]:
#             return True
#
#     for i in range(len(nums) - k):
#
#         # print(i)
#         for j in range(k+1):
#             # print(nums[s+j])
#
#             if str(nums[s+j]) in hash:
#                 # print(hash)
#                 return True
#             else:
#                 # print(hash)
#                 hash[str(nums[s+j])] = 1
#         # print(hash)
#         # print("rua")
#
#         hash = {}
#         s += 1
#     return False
#
# res = if_duplicate(nums, k)
# print(res)






