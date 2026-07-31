581. 最短无序连续子数组



def findUnsortedSubarray(self, nums: List[int]) -> int:
    n = len(nums)
    maxn, right = float("-inf"), -1
    minn, left = float("inf"), -1

    for i in range(n):
        if maxn > nums[i]:
            right = i
        else:
            maxn = nums[i]
        
        if minn < nums[n - i - 1]:
            left = n - i - 1
        else:
            minn = nums[n - i - 1]
    
    return 0 if right == -1 else right - left + 1






def findUnsortedSubarray(self, nums: List[int]) -> int:
    n = len(nums)

    def isSorted() -> bool:
        for i in range(1, n):
            if nums[i - 1] > nums[i]:
                return False
        return True
    
    if isSorted():
        return 0
    
    numsSorted = sorted(nums)
    left = 0
    while nums[left] == numsSorted[left]:
        left += 1

    right = n - 1
    while nums[right] == numsSorted[right]:
        right -= 1
    
    return right - left + 1





