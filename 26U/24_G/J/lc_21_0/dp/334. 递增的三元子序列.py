# 334. 递增的三元子序列

def increasingTriplet(self, nums: List[int]) -> bool:
    n = len(nums)
    if n < 3:
        return False
    leftMin = [0] * n
    leftMin[0] = nums[0]
    for i in range(1, n):
        leftMin[i] = min(leftMin[i - 1], nums[i])
    rightMax = [0] * n
    rightMax[n - 1] = nums[n - 1]
    for i in range(n - 2, -1, -1):
        rightMax[i] = max(rightMax[i + 1], nums[i])
    for i in range(1, n - 1):
        if leftMin[i - 1] < nums[i] < rightMax[i + 1]:
            return True
    return False



# greedy
def increasingTriplet(self, nums: List[int]) -> bool:
    n = len(nums)
    if n < 3:
        return False
    first, second = nums[0], float('inf')
    for i in range(1, n):
        num = nums[i]
        if num > second:
            return True
        if num > first:
            second = num
        else:
            first = num
    return False




def increasingTriplet(self, nums: List[int]) -> bool:
    if len(nums) < 3:
        return False
    stack = []
    for n in nums:
        while stack and n < stack[-1]:
            # stack.insert(bisect.bisect_left(stack, n), n)
            stack.pop()
        # elif not stack or stack and n > stack[-1]:
        stack.append(n)
        if len(stack) == 3:
            return True
        print(stack)
    return False





