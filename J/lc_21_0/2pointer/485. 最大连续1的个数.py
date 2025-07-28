# 485. 最大连续 1 的个数

def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
    return max(sum(g) for _, g in groupby(nums))


def findMaxConsecutiveOnes(self, nums):
    for i in range(1, len(nums)):
        if nums[i]:
            nums[i] += nums[i - 1]
    return max(nums)



def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
    max_cnt = nums[0]
    for i in range(1, len(nums)):
        if nums[i]:
            nums[i] += nums[i -1]
            max_cnt = max( nums[i], max_cnt)
    return max_cnt



def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
    l = r = 0
    con = 0
    res = 0
    for i in range(len(nums)):
        if nums[i] == 1:
            if con == 0:
                l = i
                con = 1
            r = i
            res = max(res, r - l + 1)
        else:
            con = 0
    return res


def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
    con = 0
    res = 0
    for i in range(len(nums)):
        if nums[i] == 1:
            con += 1
        else:
            res = max(res, con)
            con = 0
    res = max(res, con)
    return res


def findMaxConsecutiveOnes(self, nums):
    cnt = 0
    ans = 0
    for num in nums:
        if num == 1:
            cnt += 1
            ans = max(ans, cnt)
        else:
            cnt = 0
    return ans


def findMaxConsecutiveOnes(self, nums):
    index = -1
    res = 0
    for i, num in enumerate(nums):
        if num == 0:
            index = i
        else:
            res = max(res, i - index)
    return res






















