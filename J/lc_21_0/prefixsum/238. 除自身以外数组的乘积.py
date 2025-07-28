# 238. 除自身以外数组的乘积

def productExceptSelf(self, nums: List[int]) -> List[int]:
    length = len(nums)
    
    L, R, answer = [0]*length, [0]*length, [0]*length
    
    L[0] = 1
    for i in range(1, length):
        L[i] = nums[i - 1] * L[i - 1]
    
    R[length - 1] = 1
    for i in reversed(range(length - 1)):
        R[i] = nums[i + 1] * R[i + 1]

    for i in range(length):
        answer[i] = L[i] * R[i]
    
    return answer

def productExceptSelf(self, nums: List[int]) -> List[int]:
    length = len(nums)
    answer = [0]*length
    
    answer[0] = 1
    for i in range(1, length):
        answer[i] = nums[i - 1] * answer[i - 1]
    
    R = 1;
    for i in reversed(range(length)):
        answer[i] = answer[i] * R
        R *= nums[i]
    
    return answer


def productExceptSelf(self, nums: List[int]) -> List[int]:
    n = len(nums)
    pre = [1] * n
    suf = [1] * n
    res = [0] * n
    for i in range(1, n):
        pre[i] = pre[i-1] * nums[i-1]
        suf[n-i-1] = suf[n-i] * nums[n-i]
    for i in range(n):
        res[i] = pre[i] * suf[i]
    return res



def productExceptSelf(self, nums: [int]) -> [int]:
    res, p, q = [1], 1, 1
    for i in range(len(nums) - 1): # bottom triangle
        p *= nums[i]
        res.append(p)
    for i in range(len(nums) - 1, 0, -1): # top triangle
        q *= nums[i]
        res[i - 1] *= q
    return res























