#!/usr/bin/env python
# coding: utf-8

# In[42]:


a = list(range(7))
a


# In[2]:


A, B = 1, 2
a = (A, B)
a


# In[37]:


def rtt(nums, k):
    a = nums[-k:]
    print(a)
    b = nums[:-k]
    print(b)
    c = a + b
    return c


# In[48]:


def rtt(nums, k):
    a = nums[-k:]
    print(a)
    b = nums[:-k]
    print(b)
    nums[:] = a + b #
    print(nums)


# In[49]:


b = rtt(a, 3)
b


# In[10]:


class Solution:
    # @param nums, a list of integer
    # @param k, num of steps
    # @return nothing, please modify the nums list in-place.
    # %
    def rotate(self, nums, k):
        n = len(nums)
        k = k % n
        nums[:] = nums[n-k:] + nums[:n-k]
        return nums


# In[15]:


b = s.rotate(_, a, 2)
b


# In[ ]:


# Classical 3-step array rotation:
# reverse the first n - k elements
# reverse the rest of them
# reverse the entire array
# O(n) in time, O(1) in space
def rotate(self, nums, k):
        if k is None or k <= 0: #None, Null, not
            return
        k, end = k % len(nums), len(nums) - 1
        self.reverse(nums, 0, end - k)
        self.reverse(nums, end - k + 1, end)
        self.reverse(nums, 0, end)
        
    def reverse(self, nums, start, end):
        while start < end:
            nums[start], nums[end] = nums[end], nums[start]
            start, end = start + 1, end - 1


# In[ ]:


# Rotate k times:
# Each rotation, we move the n - 1 to the back of the array 
# one by one and we do rotation k times.
# O(n^2) in time, O(1) in space

class Solution(object):
    def rotate(self, nums, k):
        k = k % len(nums)
        for i in xrange(0, k):
            tmp = nums[-1]
            for j in xrange(0, len(nums) - 1):
                nums[len(nums) - 1 - j] = nums[len(nums) - 2 - j]
            nums[0] = tmp


# In[ ]:


# Recursive solution
# put the shorter part in the correct position then do the rest of them iteratively. 
# This is not necessarily to be a recursive solution.
# O(n) in time, O(n) in space

class Solution(object):
    def rotate(self, nums, k):
        self.helper(0, len(nums) - 1 - (k % len(nums)), len(nums) - 1, nums) # mid belongs to left part

    def helper(self, start, mid, end, nums):
        left, right = mid - start, end - mid - 1
        if left < 0 or right < 0:
            return
        if left > right:
            for j in xrange(mid + 1, end + 1):
                nums[j], nums[start] = nums[start], nums[j]
                start += 1
            self.helper(start, mid, end, nums)
        elif right >= left:
            i = mid
            while i >= start:
                nums[i], nums[end] = nums[end], nums[i]
                i, end = i - 1, end - 1
            if left != right:
                self.helper(start, mid, end, nums)


# In[ ]:


# Iterative and improved solution:
# put the last k elements in correct position (ahead) 
# and do the remaining n - k. Once finish swap, the n and k decrease.
# O(n) in time, O(1) in space

class Solution(object):
    def rotate(self, nums, k):
        """
        :type nums: List[int]
        :type k: int
        :rtype: void Do not return anything, modify nums in-place instead.
        """
        n, k, j = len(nums), k % len(nums), 0
        while n > 0 and k % n != 0:
            for i in xrange(0, k):
                nums[j + i], nums[len(nums) - k + i] = nums[len(nums) - k + i], nums[j + i] # swap
            n, j = n - k, j + k
            k = k % n


# In[ ]:


class Solution(object):
    def rotate(self, nums, k):
        """
        :type nums: List[int]
        :type k: int
        :rtype: void Do not return anything, modify nums in-place instead.
        """
        k=k%len(nums)
        if k==0:
            return
        first=nums[:-k]
        second=nums[-k:]
        for i in range(k):
            nums[i]=second[i]
        for i in range(k,len(nums)):
            nums[i]=first[i-k]


# In[ ]:


# slow due to insert/pop
class Solution:
    def rotate(self, nums, k):
        while k > 0:
            nums.insert(0, nums.pop())
            k -= 1


# In[ ]:


from collections import deque

class Solution:
    def rotate(self, nums, k):
        d = deque(nums)
        d.rotate(k)
        nums[:] = list(d)

