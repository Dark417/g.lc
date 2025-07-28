"""
Given an array nums and a value val, remove all instances of that value in-place and return the new length.

Do not allocate extra space for another array, you must do this by modifying the input array in-place with O(1) extra memory.

The order of elements can be changed. It doesn't matter what you leave beyond the new length.

Example 1:

Given nums = [3,2,2,3], val = 3,

Your function should return length = 2, with the first two elements of nums being 2.

It doesn't matter what you leave beyond the returned length.
Example 2:

Given nums = [0,1,2,2,3,0,4,2], val = 2,

Your function should return length = 5, with the first five elements of nums containing 0, 1, 3, 0, and 4.

Note that the order of those five elements can be arbitrary.

It doesn't matter what values are set beyond the returned length.
Clarification:

Confused why the returned value is an integer but your answer is an array?

Note that the input array is passed in by reference, which means modification to the input array will be known to the caller as well.

Internally you can think of this:

// nums is passed in by reference. (i.e., without making a copy)
int len = removeElement(nums, val);

// any modification to nums in your function would be known by the caller.
// using the length returned by your function, it prints the first len elements.
for (int i = 0; i < len; i++) {
    print(nums[i]);


I wanted to swap, but whatf all are to be reoved
"""


def removeElement(self, nums: List[int], val: int) -> int:
    i = 0
    for j in range(len(nums)):
        if nums[j] != val:
            nums[i] = nums[j]
            i += 1
    return i


def removeElement(self, nums: List[int], val: int) -> int:
    i, j = 0, len(nums)
    while i < j:
        if nums[i] == val:
            nums[i] = nums[j-1]
            j -= 1
        else:
            i += 1
    return i




def removeElement(self, nums: List[int], val: int) -> int:
    i, j = 0, len(nums)-1
    while i <= j:
        if nums[i] == val:
            nums[i] = nums[j]
            j -= 1
        else:
            i += 1
    return i





def removeElement(self, nums: List[int], val: int) -> int:
    i, j = 0, 0
    while i < len(nums):
        if nums[i] != val:
            nums[j] = nums[i]
            i += 1
            j += 1
        else:
            i += 1
    return j




def removeElement(self, nums: List[int], val: int) -> int:
    i, j = 0, 0
    while i < len(nums)-j: #用j代表列表中与目标值相同的个数，len(nums)-j为尾部指针
        if nums[i] == val:
            j += 1
            nums[i] = nums[-j]
        else:
            i += 1
    return len(nums)-j












def removeElement(self, nums, val):
    while True:
        try:
            a = nums.index(val)
        except: break
        nums.pop(a)
    return len(nums)



def removeElement(self, nums: List[int], val: int) -> int:
    a = nums.count(val)
    for i in range(a):
        nums.remove(val)
    return len(nums)



def removeElement(self, nums, val):
    try:
        while True:
            nums.remove(val)
    except:
        return len(nums)



def removeElement(self, nums, val):
    for x in nums[:]:
        if x == val:
            nums.remove(val)
    return len(nums)



def removeElement(self, nums, val):
    while val in nums:
        nums.pop(nums.index(val))
    return len(nums)








def removeElement(self, nums, val):
    i = 0
    for x in nums:
        if x != val:
            nums[i] = x
            i += 1
    return i




def removeElement(self, nums, val):
    start, end = 0, len(nums) - 1
    while start <= end:
        if nums[start] == val:
            nums[start], nums[end], end = nums[end], nums[start], end - 1
        else:
            start +=1
    return start




def removeElement(self, nums, val):
	start, end = 0, len(nums)-1 
    f=0
    while start <= end:
        if nums[start] == val:
            start+=1
        elif nums[end]==val:
            end-=1
        else:
            nums[f]=nums[start]
            f+=1
            start+=1
    return f



def removeElement(self, nums: List[int], val: int) -> int:
    n = 0
    while(n<len(nums)):
        if nums[n] == val:
            del nums[n]
            continue
        else:
            n += 1
    return n


def removeElement(self, nums, val):
    start, end = 0, len(nums) - 1
    while start <= end:
        if nums[start] == val:
            nums[start], nums[end], end = nums[end], nums[start], end - 1
        else:
            start +=1
    nums[:] = nums[:start]
    return start




def removeElement(self, nums: List[int], val: int) -> int:
    start, end = 0, len(nums)-1
    
    while start <= end:
        if nums[start] == val:
            # temp = nums[start]
            # nums[start] = nums[end]
            # nums[end] = temp
			nums[start], nums[end] = nums[end], nums[start]  # This is equal to three previous lines
            end -= 1
        else:
            start += 1
    
    return start






"""
def removeElement(self, nums: List[int], val: int) -> int:
    if not nums: return 0
    i,j = 0, len(nums)-1
    while i!=j:
        while nums[i] == val:
            nums[i], nums[j] = nums[j], nums[i]
            j -= 1
        i += 1
    return len(nums[:j+1])
"""


















































































































