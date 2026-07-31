"""
203.283. Move Zeroes
移动零


Given an array nums, write a function to move all 0's to the end of it while maintaining the relative order of the non-zero elements.

Example:

Input: [0,1,0,3,12]
Output: [1,3,12,0,0]
Note:

You must do this in-place without making a copy of the array.
Minimize the total number of operations.


return None
nums = nums[::-1]  ? doesn't work

"""

def moveZeroes(self, nums: List[int]) -> None:
    i = j = 0
    while j < len(nums):
        if nums[j] != 0:
            nums[i] = nums[j]
            i += 1
        j += 1
    nums[i:] = [0] * (len(nums)-i)


# nb
def moveZeroes(self, nums):
    if not nums:
        return 0
    j = 0
    for i in range(len(nums)):
        if nums[i]:
            nums[j],nums[i] = nums[i],nums[j]
            j += 1



def moveZeroes(self, nums: List[int]) -> None:
    n = len(nums)
    left = right = 0
    while right < n:
        if nums[right] != 0:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
        right += 1




def moveZeroes(self, nums: List[int]) -> None:
	i = c = 0
    while i < len(nums):
        if c == len(nums) - i -1:
            break
        if nums[i] == 0:
            nums.append(nums.pop(i))
            c += 1
        else:
            i += 1


def moveZeroes(self, nums: List[int]) -> None:
    i = 0
    for j in range(len(nums)):
        if nums[j] != 0:
            nums[i] = nums[j]
            i += 1
    nums[i:] = [0]*len(nums[i:])



def moveZeroes(self, nums):
	if not nums: return 0
	# 两个指针i和j
	j = 0
	for i in xrange(len(nums)):
		# 当前元素!=0，就把其交换到左边，等于0的交换到右边
		if nums[i]:
			nums[j],nums[i] = nums[i],nums[j]
			j += 1

	pos = 0
    for i in range(len(nums)):
        el = nums[i]
        if el != 0:
            nums[pos], nums[i] = nums[i], nums[pos]
            pos += 1

    i = count = 0
    while count < len(nums):
        if nums[i] == 0: nums.append(nums.pop(i))
        else: i += 1
        count += 1


 
def moveZeroes(self, nums):
	if not nums: return 0
	j = 0
	for i in range(len(nums)):
		if nums[i]:
			if i > j:
				nums[j] = nums[i]
				nums[i] = 0
			j += 1
# if not 0, sync
# if not sync, non-zero in the gap






def moveZeroes(self, nums: List[int]) -> None:
    for i in range(nums.count(0)):
        nums.remove(0)
        nums.append(0)



def moveZeroes(self, nums: List[int]) -> None:
    nums.sort(key=bools, reverse=True)




def moveZeroes(self, nums: List[int]) -> None:
    n = len(nums)
    index = 0
    for i in range(n):
        if not nums[i]:
            index = min(index, i)
        else:
            nums[i], nums[index] = nums[index], nums[i]
            index += 1




def moveZeroes(self, nums: List[int]) -> None:
    try:
        count = 0
        while True:
            nums.remove(0)
            count += 1
    except:
        nums += count * [0]

















































