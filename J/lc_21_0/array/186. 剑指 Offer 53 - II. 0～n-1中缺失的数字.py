"""
186. 剑指 Offer 53 - II. 0～n-1中缺失的数字


一个长度为n-1的递增排序数组中的所有数字都是唯一的，并且每个数字都在范围0～n-1之内。在范围0～n-1内的
n个数字中有且只有一个数字不在该数组中，请找出这个数字。

 

示例 1:

输入: [0,1,3]
输出: 2
示例 2:

输入: [0,1,2,3,4,5,6,7,9]
输出: 8

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/que-shi-de-shu-zi-lcof
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

"""

def missingNumber(self, nums: List[int]) -> int:
    i, j = 0, len(nums) - 1
    while i <= j:
        m = (i + j) // 2
        if nums[m] == m:
        	i = m + 1
        else:
        	j = m - 1
    return i





def missingNumber(self, nums: List[int]) -> int:
    n=len(nums)+1
    L=[i for i in range(n)]
    L1=list(set(L)-set(nums))
    return L1[0]


def missingNumber(self, nums: List[int]) -> int:
    if nums[0] != 0: return 0
    for i in range(len(nums)):
        if nums[i] != i:
            return i
    return len(nums)


def missingNumber(self, nums):\
    #求和作差，缺失的即为不在的数字
    l = len(nums)
    maxsum = l*(l+1)/2
    arrsum = sum(nums)
    return maxsum - arrsum


def missingNumber(self, nums):
    if len(nums) == (nums[-1]+1):
        return nums[-1]+1
    for i in range(nums[-1]):
        if i != nums[i]:
            return i



def missingNumber(self, nums):
    #作差,计算出现差值为2时的作差次数

    #特殊情况1：长度为1
    if len(nums) == 1: return 1 if nums[0] == 0 else 0
    #特殊情况2：长度为0
    if len(nums) == 0: return 0  
    #特殊情况3：连续数组缺最大数
    if nums[-1] == len(nums)-1: return len(nums)
    #特殊情况4：连续数组缺最小数
    if nums[0] != 0: return 0
    
    count = 0
    for i in range(1, len(nums)):
        count += 1
        if nums[i] - nums[i-1] == 2:
            return count
































































































