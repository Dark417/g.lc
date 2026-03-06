# 169. 多数元素


def majorityElement(self, nums: List[int]) -> int:
    count = 0
    candidate = None

    for num in nums:
        if count == 0:
            candidate = num
        count += (1 if num == candidate else -1)

    return candidate


def majorityElement(self, nums: List[int]) -> int:
    def majority_element_rec(lo, hi) -> int:
        if lo == hi:
            return nums[lo]
		mid = (hi - lo) // 2 + lo
        left = majority_element_rec(lo, mid)
        right = majority_element_rec(mid + 1, hi)
		if left == right:
            return left
		left_count = sum(1 for i in range(lo, hi + 1) if nums[i] == left)
        right_count = sum(1 for i in range(lo, hi + 1) if nums[i] == right)
        return left if left_count > right_count else right
    return majority_element_rec(0, len(nums) - 1)



def majorityElement(self, nums: List[int]) -> int:
    majority_count = len(nums) // 2
    while True:
        candidate = random.choice(nums)
        if sum(1 for elem in nums if elem == candidate) > majority_count:
            return candidate


def majorityElement(self, nums: List[int]) -> int:
    nums.sort()
    return nums[len(nums) // 2]


def majorityElement(self, nums: List[int]) -> int:
    counts = collections.Counter(nums)
    return max(counts.keys(), key=counts.get)














