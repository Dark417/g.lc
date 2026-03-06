#!/usr/bin/env python
# coding: utf-8

# 1281. Subtract the Product and Sum of Digits of an Integer
# Given an integer number n, return the difference between the product of its digits and the sum of its digits.

# import numpy
# n = 124
# list = str(n)
# list1 = [i for i in list]
# list1
# list2 = [int(i) for i in list1]

# In[12]:


list2


# In[29]:


n = 12456


# In[30]:


def subtractProductAndSum(n: int) -> int:
        list0 = str(n)
        list1 = [i for i in list0]
        list2 = [int(i) for i in list1]
        product = numpy.prod([i for i in list2])
        sum0 = sum([i for i in list2])

        return product - sum0


# In[31]:


opt = subtractProductAndSum(n)
print(opt)


# In[ ]:




