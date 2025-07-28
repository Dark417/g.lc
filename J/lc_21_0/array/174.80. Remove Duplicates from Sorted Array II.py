"""
174.80. Remove Duplicates from Sorted Array II
删除排序数组中的重复项 II


Given a sorted array nums, remove the duplicates in-place such that duplicates appeared at most twice and return the new length.

Do not allocate extra space for another array, you must do this by modifying the input array in-place with O(1) extra memory.

Example 1:

Given nums = [1,1,1,2,2,3],

Your function should return length = 5, with the first five elements of nums being 1, 1, 2, 2 and 3 respectively.

It doesn't matter what you leave beyond the returned length.
Example 2:

Given nums = [0,0,1,1,1,1,2,3,3],

Your function should return length = 7, with the first seven elements of nums being modified to 0, 0, 1, 1, 2, 3 and 3 respectively.

It doesn't matter what values are set beyond the returned length.
Clarification:

Confused why the returned value is an integer but your answer is an array?

Note that the input array is passed in by reference, which means modification to the input array will be known to the caller as well.

Internally you can think of this:

// nums is passed in by reference. (i.e., without making a copy)
int len = removeDuplicates(nums);

// any modification to nums in your function would be known by the caller.
// using the length returned by your function, it prints the first len elements.
for (int i = 0; i < len; i++) {
    print(nums[i]);
}


"""



def removeDuplicates(self, nums: List[int]) -> int:
    i=j=count=0
    while i < len(nums):
        if nums[j] == nums[i] and count <= 2:
            j += 1
            count += 1
        elif j < len(nums) and nums[j] == nums[i] and count > 2:
            nums.pop(nums[j])
        else:
            i = j
            count = 0
    return i




def removeDuplicates(self, nums):
    # Initialize the counter and the array index.
    i, count = 1, 1
    
    # Start from the second element of the array and process
    # elements one by one.
    while i < len(nums):
        
        # If the current element is a duplicate, 
        # increment the count.
        if nums[i] == nums[i - 1]:
            count += 1
            
            # If the count is more than 2, this is an
            # unwanted duplicate element and hence we 
            # remove it from the array.
            if count > 2:
                nums.pop(i)
                
                # Note that we have to decrement the
                # array index value to keep it consistent
                # with the size of the array.
                i-= 1
            
        else:
            
            # Reset the count since we encountered a different element
            # than the previous one
            count = 1
       
        # Move on to the next element in the array
        i += 1    
            
    return len(nums)



def removeDuplicates(self, nums):
    # Initialize the counter and the second pointer.
    j, count = 1, 1
    # Start from the second element of the array and process
    # elements one by one.
    for i in range(1, len(nums)):
        # If the current element is a duplicate, 
        # increment the count.
        if nums[i] == nums[i - 1]:
            count += 1
        else:
            # Reset the count since we encountered a different element
            # than the previous one
            count = 1
        # For a count <= 2, we copy the element over thus
        # overwriting the element at index "j" in the array
        if count <= 2:
            nums[j] = nums[i]
            j += 1
    return j




def removeDuplicates(self, nums: List[int]) -> int:
    s = 1 
    f = 2
    while f < len(nums):   
        if nums[s-1] == nums[f]:
            f+=1
        else:            
            nums[s+1] = nums[f]
            s+=1
            f+=1
    return  s+1


def removeDuplicates(self, nums: List[int]) -> int:
	i = 2
    while i<len(nums):
        if nums[i] == nums[i - 2]:
            nums.pop(i)
        else:
            i += 1
    return len(nums)





























































































































