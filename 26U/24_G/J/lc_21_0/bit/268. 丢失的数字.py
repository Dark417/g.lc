# 268. 丢失的数字


# bit
def missingNumber(self, nums):
    missing = len(nums)
    for i, num in enumerate(nums):
        missing ^= i ^ num
    return missing

    

def missingNumber(self, nums):
    nums.sort()
    if nums[-1] != len(nums):
        return len(nums)
    elif nums[0] != 0:
        return 0
    for i in range(1, len(nums)):
        expected_num = nums[i-1] + 1
        if nums[i] != expected_num:
            return expected_num



def missingNumber(self, nums):
    num_set = set(nums)
    n = len(nums) + 1
    for number in range(n):
        if number not in num_set:
            return number




def missingNumber(self, nums: List[int]) -> int:
    for i in range(max(nums)+2):
        if i not in nums:
            return i




def missingNumber(self, nums):
    expected_sum = len(nums)*(len(nums)+1)//2
    actual_sum = sum(nums)
    return expected_sum - actual_sum





def missingNumber(self, nums: List[int]) -> int:
    if len(nums) == 1 and nums[0] != 0:
        return 0
    nums.sort()
    for i in range(len(nums)):
        if i != nums[i]:
            return i
    return len(nums)


def missingNumber(self, nums: List[int]) -> int:
    for i in range(len(nums)):
        if i not in nums:
            return i
    return len(nums)




return len(nums)*(len(nums)+1)//2 - sum(nums)
return sum(range(len(nums)+1)) - sum(nums)

# set
return min({i for i in range(max(nums)+2)}^set(nums))


return reduce(operator.xor, nums + range(len(nums)+1))

return (set(range(len(nums)+1)) - set(nums)).pop()



def missingNumber(self, nums):
    n = len(nums)
    return reduce(operator.xor, nums) ^ [n, 1, n+1, 0][n % 4]






def missingNumber(self, nums):
    new = sorted(nums)
    low = 0
    high = len(new) - 1
    
    if new[high] == high:
        return len(new)

    while True:
        mid = int((low + high) /2)
        if new[mid] == mid:
            low = mid + 1
        if new[mid] > mid:
            high = mid
        if low >= high:
            return low



def missingNumber(self, nums):
    nums = sorted(nums)
    l = len(nums)
    left = 0
    right = l
    
    while (left < right):
        mid = (left + right) / 2
        if mid < nums[mid]:
            right = mid
        else:
            left = mid + 1
    return left

































