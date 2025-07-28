#!/usr/bin/env python
# coding: utf-8

# In[ ]:


You're given strings J representing the types of stones 
that are jewels, and S representing the stones you have.  
Each character in S is a type of stone you have.  You want to 
know how many of the stones you have are also jewels.

The letters in J are guaranteed distinct, and all characters 
in J and S are letters. Letters are case sensitive, so "a" is 
considered a different type of stone from "A".

S and J will consist of letters and have length at most 50.
The characters in J are distinct.


# In[38]:


len(J)


# In[35]:


for i in range(len(J)):
    print(i)


# In[ ]:


s.count(j)


# In[ ]:


sum(map(J.count, S))


# In[ ]:


sum(map(S.count, J))  


# In[ ]:


sum(s in J for s in S)


# In[ ]:


def numJewelsInStones(self, J, S):
        charToFreqS = {}  # Map character to its frequency in S.
        numJewels = 0  # Total number of jewels.
        
        for ch in S:
            if ch not in charToFreqS:
                charToFreqS[ch] = 1
            else:
                charToFreqS[ch] += 1
        
        for ch in J:
            if ch in charToFreqS:
                numJewels += charToFreqS[ch]
                
        return numJewels


# In[27]:


def fj(J, S):
    num = 0
    
    for i in list(J):
#         l = [x if x is i for i in S]
        print(i)
#         for x in S:
#             print(x)
#             if i == x:
#                 num += 1
    
    return num


# In[43]:


def fj2(J, S):
    num = 0
    for i in S:
        if i in J:
            num +=1
    return num


# In[ ]:





# In[44]:


J = "aA", 
S = "aAAbbbb"


# In[45]:


x = fj2(J, S)
x


# In[ ]:




