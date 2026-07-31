#!/usr/bin/env python
# coding: utf-8

# In[ ]:


832. Flipping an Image

Given a binary matrix A, we want to flip the image horizontally, 
then invert it, and return the resulting image.


# In[11]:


input1 = [[1,1,0],[1,0,1],[0,0,0]]
input2 = [[1,1,0,0],[1,0,0,1],[0,1,1,1],[1,0,1,0]]


# In[3]:


a = list(range(5))
mid = len(a) // 2 - 1
mid


# In[16]:


def flip(A):
    
    for i in A:
#         reverse
        if len(i)%2 == 1:
            mid = len(i) // 2 - 1
            start = 0
            end = len(i) - 1
            
            while start <= mid:
                i[start], i[end] = i[end], i[start]
                start += 1
                end -= 1
            
        
#         else:
            
            
    
#     for i in A:
#         for j in i:
#             j = 0 if j==1 else 0
    
    return A


# In[17]:


output1 = flip(input1)
output1


# In[ ]:




