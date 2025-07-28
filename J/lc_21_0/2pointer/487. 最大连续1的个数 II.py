# 487. 最大连续1的个数 II

# 问题： 重点：pre + 1 + cur;  而不是继续算con...
def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
    con = 0
    res = 0
    flip = 1
    for i in range(len(nums)):
        if nums[i] == 1:
            con += 1
        else:
            if flip == 1:
                flip = 0
                con += 1
                
            else:
                res = max(res, con)
                con = 0
                flip = -1
    res = max(res, con)
    return res


# dp
def findMaxConsecutiveOnes(self, nums):
    dp0 = 0
    dp1 = 0
    result = 0
    for num in nums:
        if num == 0:
            dp1 = dp0 + 1
            dp0 = 0
        else:
            dp1 += 1
            dp0 += 1
        result = max(result, dp0, dp1)
    return result




def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
    res, prev, cnt = 0, 0, 0
    for num in nums:
        cnt += 1
        if num == 0:
            prev = cnt
            cnt = 0
        res = max(res, prev + cnt)
    return res




def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
    left = 0
    res = 0
    cur_zero_num = 0
    for right in range(len(nums)):
        if nums[right] == 0:
            cur_zero_num += 1
        while cur_zero_num > 1:
            if nums[left] == 0:
                cur_zero_num -= 1
            left += 1
        res = max(res, right - left + 1)
    return res



def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
    left = 0
    res = 0
    cur_zero_num = 0
    queue = collections.deque()
    for right in range(len(nums)):
        if nums[right] == 0:
            cur_zero_num += 1
            queue.appendleft(right)
        while cur_zero_num > 1:
            left = queue.pop() + 1
            cur_zero_num -= 1
        res = max(res, right - left + 1)
    return res



def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
    n = len(nums)
    pre = 0
    i = 0
    res = 0
    while i < n:
        j = i 
        while j + 1 < n and nums[j + 1] == 1:
            j += 1
        res = max(res, pre + j - i + 1)
        pre = j - i + 1 if nums[i] == 1 else j - i
        i = j + 1
    return res



















