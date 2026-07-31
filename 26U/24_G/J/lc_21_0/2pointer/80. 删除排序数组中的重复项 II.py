# 80. 删除排序数组中的重复项 II


def removeDuplicates(self, nums):
	i = 0
	for n in nums:
		if i < 2 or n > nums[i - 2]:
			nums[i] = 0
			i += 1
	return i


def removeDuplicates(self, nums):
    pos = 0
    for i in range(0, len(nums)):
        if i == 0 or nums[i-1] != nums[i]:
            nums[pos] = nums[i]
            pos += 1
    return pos


def removeDuplicates(self, nums):
    j, count = 1, 1
    for i in range(1, len(nums)):
        if nums[i] == nums[i - 1]:
            count += 1
        else:
            count = 1
        if count <= 2:
            nums[j] = nums[i]
            j += 1
    return j



def removeDuplicates(self, nums):
	if len(nums) < 2: return len(nums)
    slow, fast = 2, 2

    while fast < len(nums):
        if nums[slow - 2] != nums[fast]:
            nums[slow] = nums[fast]
            slow += 1
        fast += 1
    return slow




def removeDuplicates(self, nums ):
    i, count = 1, 1
    while i < len(nums):
        if nums[i] == nums[i - 1]:
            count += 1
            if count > 2:
                nums.pop(i)
                i-= 1
        else:
            count = 1
        i += 1      
    return len(nums)


























