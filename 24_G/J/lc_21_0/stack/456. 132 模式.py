# 456. 132 模式

def find132pattern(self, nums):
    N = len(nums)
    numsi = nums[0]
    for j in range(1, N):
        for k in range(N - 1, j, -1):
            if numsi < nums[k] and nums[k] < nums[j]:
                return True
        numsi = min(numsi, nums[j])
    return False


def find132pattern(self, nums):
    import sys
    stack = []
    s3 = -sys.maxint
    for n in nums[::-1]:
        if n < s3:
            return True
        while stack and stack[-1] < n:
            s3 = stack.pop()
        stack.append(n)
    return False


def find132pattern(self, nums: List[int]) -> bool:
    stk, maxmid = [], float('-inf')
    for n in nums[::-1]:
        if n < maxmid: 
            return True
        while stk and stk[-1] < n:
            maxmid = stk.pop()
        stk += n,
    
    return False

    

def find132pattern(self, nums):
    N = len(nums)
    leftMin = [float("inf")] * N
    for i in range(1, N):
        leftMin[i] = min(leftMin[i - 1], nums[i - 1])
    stack = []
    for j in range(N - 1, -1, -1):
        numsk = float("-inf")
        while stack and stack[-1] < nums[j]:
            numsk = stack.pop()
        if leftMin[j] < numsk:
            return True
        stack.append(nums[j])
    return False



def find132pattern(self, nums: List[int]) -> bool:
    stack = []
    k = -(10 ** 9 + 7)
    for i in range(len(nums) - 1,-1,-1):
        if nums[i] < k:
            return True
        while stack and stack[-1] < nums[i]:
            k = max(k,stack.pop())
        stack.append(nums[i])
    return False


def find132pattern(self, nums: List[int]) -> bool:
    n = len(nums)
    candidate_k = [nums[n - 1]]
    max_k = float("-inf")

    for i in range(n - 2, -1, -1):
        if nums[i] < max_k:
            return True
        while candidate_k and nums[i] > candidate_k[-1]:
            max_k = candidate_k[-1]
            candidate_k.pop()
        if nums[i] > max_k:
            candidate_k.append(nums[i])

    return False



# bisect
def find132pattern(self, nums: List[int]) -> bool:
    n = len(nums)
    if n < 3:
        return False
    
    left_min = nums[0]
    right_all = SortedList(nums[2:])
    
    for j in range(1, n - 1):
        if left_min < nums[j]:
            index = right_all.bisect_right(left_min)
            if index < len(right_all) and right_all[index] < nums[j]:
                return True
        left_min = min(left_min, nums[j])
        right_all.remove(nums[j + 1])

    return False



def find132pattern(self, nums):
    min_list = list(accumulate(nums, min))
    stack, n = [], len(nums)
    
    for j in range(n-1, -1, -1):
        if nums[j] > min_list[j]:
            while stack and stack[-1] <= min_list[j]:
                stack.pop()
            if stack and stack[-1] < nums[j]:
                return True
            stack.append(nums[j])           
    return False






#???
def find132pattern(self, nums: List[int]) -> bool:
    candidate_i, candidate_j = [-nums[0]], [-nums[0]]

    for v in nums[1:]:
        idx_i = bisect.bisect_right(candidate_i, -v)
        idx_j = bisect.bisect_left(candidate_j, -v)
        if idx_i < idx_j:
            return True

        if v < -candidate_i[-1]:
            candidate_i.append(-v)
            candidate_j.append(-v)
        elif v > -candidate_j[-1]:
            last_i = -candidate_i[-1]
            while candidate_j and v > -candidate_j[-1]:
                candidate_i.pop()
                candidate_j.pop()
            candidate_i.append(-last_i)
            candidate_j.append(-v)

    return False







def find132pattern(self, nums: List[int]) -> bool:
    if len(set(nums)) < 3:
        return False

    min_nums = [nums[0]]
    for i in range(1, len(nums)):
        min_nums.append(min(nums[i], min_nums[-1]))
        
    stack = []  
    i = len(nums) - 1
    for i in range(len(nums)-1, -1, -1):
        if( nums[i] > min_nums[i] ):
            while( stack and stack[-1] <= min_nums[i] ):
                stack.pop()
            if(stack and min_nums[i] < stack[-1] < nums[i] ):
                return True
            stack.append(nums[i])
    return False   