# 26. 删除排序数组中的重复项


"""
public int removeDuplicates(int[] nums) {
    int i = nums.length > 0 ? 1 : 0;
    for (int n : nums)
        if (n > nums[i-1])
            nums[i++] = n;
    return i;
}

"""


def removeDuplicates(self, nums: List[int]) -> int:
    if not nums: return 0
    i = 0 
    for j in range(1, len(nums)):
        if nums[i] != nums[j]:
            i += 1
            nums[i] = nums[j]
    return i + 1



x = 1
for i in range(len(nums)-1):
	if(nums[i]!=nums[i+1]):
		nums[x] = nums[i+1]
		x+=1
return(x)



def removeDuplicates(self, nums: List[int]) -> int:
    if not nums:
        return 0
    i = j = 0
    a = nums[i]
    while i < len(nums):
        if nums[j] != nums[i]:
            j += 1
            nums[j] = nums[i]
        i += 1
    print(nums)
    return j + 1


from collections import OrderedDict
def removeDuplicates(self, nums):
    nums[:] =  OrderedDict.fromkeys(nums).keys()
    return len(nums)


def removeDuplicates(self, nums):
    nums[:] = sorted(set(nums))
    return len(nums)































































