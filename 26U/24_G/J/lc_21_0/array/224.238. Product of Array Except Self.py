"""
224.238. Product of Array Except Self
剑指 Offer 66. 构建乘积数组
除自身以外数组的乘积

Given an array nums of n integers where n > 1,  return an array output such that 
output[i] is equal to the product of all the elements of nums except nums[i].

Example:

Input:  [1,2,3,4]
Output: [24,12,8,6]
Constraint: It's guaranteed that the product of the elements of any prefix or suffix 
of the array (including the whole array) fits in a 32 bit integer.

Note: Please solve it without division and in O(n).

Follow up:
Could you solve it with constant space complexity? (The output array does not count as 
extra space for the purpose of space complexity analysis.)


"""


def productExceptSelf(self, nums: List[int]) -> List[int]:
    res0 = res1 = 1
    l1, l2 = [1], [1]
    for i in range(len(nums)-1):
        res0 *= nums[i]
        res1 *= nums[len(nums)-i-1]
        l1.append(res0)
        l2.append(res1)
    l2 = l2[::-1]
    for i in range(len(l1)):
    	l1[i] = l1[i] * l2[len(l2)-i-1]
        #l1[i] = l1[i] * l2[i]
    return l1


def productExceptSelf(self, nums: [int]) -> [int]:
	if not nums: return []
    res, p, q = [1], 1, 1
    for i in range(len(nums) - 1): # bottom triangle
        p *= nums[i]
        res.append(p)
    for i in range(len(nums) - 1, 0, -1): # top triangle
        q *= nums[i]
        res[i - 1] *= q
    return res



# official

def productExceptSelf(self, nums: List[int]) -> List[int]:
    length = len(nums)
    answer = [0]*length
    
    # answer[i] 表示索引 i 左侧所有元素的乘积
    # 因为索引为 '0' 的元素左侧没有元素， 所以 answer[0] = 1
    answer[0] = 1
    for i in range(1, length):
        answer[i] = nums[i - 1] * answer[i - 1]
    
    # R 为右侧所有元素的乘积
    # 刚开始右边没有元素，所以 R = 1
    R = 1
    for i in reversed(range(length)):
        # 对于索引 i，左边的乘积为 answer[i]，右边的乘积为 R
        answer[i] = answer[i] * R
        # R 需要包含右边所有的乘积，所以计算下一个结果时需要将当前值乘到 R 上
        R *= nums[i]
    
    return answer



def productExceptSelf(self, nums: List[int]) -> List[int]:
    length = len(nums)
    
    # L 和 R 分别表示左右两侧的乘积列表
    L, R, answer = [0]*length, [0]*length, [0]*length
    
    # L[i] 为索引 i 左侧所有元素的乘积
    # 对于索引为 '0' 的元素，因为左侧没有元素，所以 L[0] = 1
    L[0] = 1
    for i in range(1, length):
        L[i] = nums[i - 1] * L[i - 1]
    
    # R[i] 为索引 i 右侧所有元素的乘积
    # 对于索引为 'length-1' 的元素，因为右侧没有元素，所以 R[length-1] = 1
    R[length - 1] = 1
    for i in reversed(range(length - 1)):
        R[i] = nums[i + 1] * R[i + 1]

    # 对于索引 i，除 nums[i] 之外其余各元素的乘积就是左侧所有元素的乘积乘以右侧所有元素的乘积
    for i in range(length):
        answer[i] = L[i] * R[i]
    
    return answer

























































