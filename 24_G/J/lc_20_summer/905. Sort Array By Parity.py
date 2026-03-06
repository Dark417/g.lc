#!/usr/bin/env python
# coding: utf-8

# In[ ]:


905. Sort Array By Parity

Given an array A of non-negative integers, return an array consisting of all the even elements of A, followed by all the odd elements of A.

You may return any answer array that satisfies this condition.


# In[5]:


if 3 % 2 == 1:
    print('rua')


# In[24]:


input = [3,1,2,4]


# In[7]:


def sortbyp(A):
    even = []
    odd = []
    for i in A:
        md = i % 2
        if md == 0:
            even.append(i)
        else:
            odd.append(i)
    B = even + odd
    return B


# In[25]:


def sortbyp(A):
    
    pivot = 0
    bp = len(A)-1
    swap = 0
    
    while pivot + 1 < bp:
        
        if A[pivot] % 2 == 1:
            
            if A[bp] % 2 == 0:
                swap = A[bp]
                A[bp] = A[pivot]
                A[pivot] = swap
                bp -= 1
            else:
                bp -= 1
                
        else:
            pivot += 1
    
    return A


# In[26]:


output = sortbyp(input)
output


# In[ ]:


def sortArrayByParity(self, A):
        """
        :type A: List[int]
        :rtype: List[int]
        """
        start = 0
        end = len(A) - 1
        while start < end:
            if A[start] % 2 != 0:
                odd = A[start]
                A[start] = A[end]
                A[end] = odd
                end -= 1
            else:
                start += 1
        return A


# In[ ]:


def sortArrayByParity(self, A):
    """
    :type A: List[int]
    :rtype: List[int]
    """
    size = len(A)
    res = [None] * size
    start = 0
    end = size - 1
    for val in A:
        if val % 2 == 1:
            res[end] = val
            end = end -1
        else:
            res[start] = val
            start = start + 1
    return res


# In[ ]:


def sortArrayByParity(self, A):
    """
    :type A: List[int]
    :rtype: List[int]
    """
    start, end = 0, len(A) - 1
    while start < end:
        m, n = A[start], A[end]
        if m % 2 == 1 and n % 2 == 0:
            A[start], A[end] = n, m
        elif m % 2 == 1:
            end -= 1
        elif n % 2 == 0:
            start += 1
        else:
            start += 1
            end -= 1
    return A


# In[ ]:


return sorted(A, key=lambda x: x % 2)


# In[ ]:


return([i for i in A if i%2==0]+[i for i in A if i%2!=0])


# In[ ]:


def sortArrayByParity(self, A):
        """
        :type A: List[int]
        :rtype: List[int]
        """
        current = 0
        for i, el in enumerate(A):
            if not el % 2:
                A[current], A[i] = A[i], A[current]
                current = current + 1
        return A


# In[ ]:


def sortArrayByParity(self, A):
        """
        :type A: List[int]
        :rtype: List[int]
        """
        start = 0
        end = len(A) - 1
        while start < end:
            if A[start] % 2 != 0:
                odd = A[start]
                A[start] = A[end]
                A[end] = odd
                end -= 1
            else:
                start += 1
        return A

