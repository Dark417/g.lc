# 18. 四数之和

# e official 2pointer
def fourSum(self, nums: List[int], target: int) -> List[List[int]]:
    def kSum(nums: List[int], target: int, k: int) -> List[List[int]]:
        res = []
        if len(nums) == 0 or nums[0] * k > target or target > nums[-1] * k:
            return res
        if k == 2:
            return twoSum(nums, target)
        for i in range(len(nums)):
            if i == 0 or nums[i - 1] != nums[i]:
                for _, set in enumerate(kSum(nums[i + 1:], target - nums[i], k - 1)):
                    res.append([nums[i]] + set)
        return res

    def twoSum(nums: List[int], target: int) -> List[List[int]]:
        res = []
        lo, hi = 0, len(nums) - 1
        while (lo < hi):
            sum = nums[lo] + nums[hi]
            if sum < target or (lo > 0 and nums[lo] == nums[lo - 1]):
                lo += 1
            elif sum > target or (hi < len(nums) - 1 and nums[hi] == nums[hi + 1]):
                hi -= 1
            else:
                res.append([nums[lo], nums[hi]])
                lo += 1
                hi -= 1
        return res

    nums.sort()
    return kSum(nums, target, 4)



# e official hashset
def fourSum(self, nums: List[int], target: int) -> List[List[int]]:
    def kSum(nums: List[int], target: int, k: int) -> List[List[int]]:
        if len(nums) == 0 or nums[0] * k > target or target > nums[-1] * k:
            return []
        if k == 2:
            return twoSum(nums, target)
        res = []
        for i in range(len(nums)):
            if i == 0 or nums[i - 1] != nums[i]:
                for _, set in enumerate(kSum(nums[i + 1:], target - nums[i], k - 1)):
                    res.append([nums[i]] + set)
        return res

    def twoSum(nums: List[int], target: int) -> List[List[int]]:
        res = []
        s = set()
        for i in range(len(nums)):
            if len(res) == 0 or res[-1][1] != nums[i]:
                if target - nums[i] in s:
                    res.append([target - nums[i], nums[i]])
            s.add(nums[i])
        return res

    nums.sort()
    return kSum(nums, target, 4)





def fourSum(self, nums: List[int], target: int) -> List[List[int]]:
    quadruplets = list()
    if not nums or len(nums) < 4:
        return quadruplets
    
    nums.sort()
    length = len(nums)
    for i in range(length - 3):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        if nums[i] + nums[i + 1] + nums[i + 2] + nums[i + 3] > target:
            break
        if nums[i] + nums[length - 3] + nums[length - 2] + nums[length - 1] < target:
            continue
        for j in range(i + 1, length - 2):
            if j > i + 1 and nums[j] == nums[j - 1]:
                continue
            if nums[i] + nums[j] + nums[j + 1] + nums[j + 2] > target:
                break
            if nums[i] + nums[j] + nums[length - 2] + nums[length - 1] < target:
                continue
            left, right = j + 1, length - 1
            while left < right:
                total = nums[i] + nums[j] + nums[left] + nums[right]
                if total == target:
                    quadruplets.append([nums[i], nums[j], nums[left], nums[right]])
                    while left < right and nums[left] == nums[left + 1]:
                        left += 1
                    left += 1
                    while left < right and nums[right] == nums[right - 1]:
                        right -= 1
                    right -= 1
                elif total < target:
                    left += 1
                else:
                    right -= 1
    
    return quadruplets



# backtrace
def fourSum(self, nums: List[int], target: int) -> List[List[int]]:
    nums.sort()
    output = []
    
    def Search(i, target, oneSolution, notSelected):
        if target == 0 and len(oneSolution) == 4:
            output.append(oneSolution)
            return
        elif len(oneSolution) > 4 or i >= len(nums):
            return

        if target - nums[i] - (3 - len(oneSolution)) * nums[-1] > 0 or nums[i] in notSelected:
            Search(i + 1, target, oneSolution, notSelected)
        elif target - (4 - len(oneSolution)) * nums[i] < 0:
            return
        else:
            Search(i + 1, target, oneSolution, notSelected + [nums[i]])
            Search(i + 1, target - nums[i], oneSolution + [nums[i]], notSelected)


    Search(0, target, [], [])

    return output






























