# 448. 找到所有数组中消失的数字

def findDisappearedNumbers(self, nums: List[int]) -> List[int]:
    n = len(nums)
    for num in nums:
        x = (num - 1) % n
        nums[x] += n
    
    ret = [i + 1 for i, num in enumerate(nums) if num <= n]
    return ret


def findDisappearedNumbers(self, nums):
    counter = set(nums)
    N = len(nums)
    res = []
    for i in range(1, N + 1):
        if i not in counter:
            res.append(i)
    return res


def findDisappearedNumbers(self, nums):
    for i, num in enumerate(nums):
        if nums[abs(num) - 1] > 0:
            nums[abs(num) - 1] *= -1
    res = []
    for i in range(len(nums)):
        if nums[i] > 0:
            res.append(i + 1)
    return res


def findDisappearedNumbers(self, nums: List[int]) -> List[int]:
    i = 0
    while i < len(nums):
        if nums[i] == i + 1:
            i += 1
            continue
        idx = nums[i] - 1
        if nums[i] == nums[idx]:
            i += 1
            continue
        nums[i], nums[idx] = nums[idx], nums[i]
    return [i + 1 for i in range(len(nums)) if nums[i] != i + 1]
	









