# 35. 搜索插入位置



# binary search
l, r = 0, n  
while l < r:
	mid = (l + r) // 2
	if x <= mid:
		r = mid  
	else:
		l = mid + 1
return l


l, r = 0, n-1
while l <= r:
	mid = (l + r) // 2
	if x <= mid:
		r = mid - 1
	else:
		l = mid + 1
return l


mid = (l + r) >> 1
mid = (l + r + 1) >> 1


mid = l + (r - l) // 2
mid = l + (r - l + 1) // 2

mid = l + ((r - l) >>1 )


def searchInsert(self, nums: List[int], target: int) -> int:
    # Log(n)
    l, r = 0, len(nums) - 1
    
    while l <= r:
        mid = (l + r) // 2
        
        if target == nums[mid]:
            return mid
        
        if target > nums[mid]:
            l = mid + 1
        else:
            r = mid - 1
    
    return l


def searchInsert(self, nums: List[int], target: int) -> int:
    size = len(nums)
    if size == 0:
        return 0

    if nums[size - 1] < target:
        return size

    left = 0
    right = size - 1

    while left < right:
        mid = (left + right) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left


def searchInsert(self, nums: List[int], target: int) -> int:
    size = len(nums)
    if size == 0:
        return 0

    # 特判
    if nums[size - 1] < target:
        return size

    left = 0
    right = size - 1

####or
    left = 0
    # 因为有可能数组的最后一个元素的位置的下一个是我们要找的，故右边界是 len
    right = size

    while left < right:
        # left + right 在 Python 中如果发生整型溢出，Python 会自动转成长整形
        mid = (left + right) // 2
        # 严格小于 target 的元素一定不是解
        if nums[mid] < target:
            # 下一轮搜索区间是 [mid + 1, right]
            left = mid + 1
        else:
            right = mid
    return left































