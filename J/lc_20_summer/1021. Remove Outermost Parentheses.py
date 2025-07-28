#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"(()())(())"


# In[ ]:


'(()())(())(()(()))'


# In[8]:


str2 = '()()'
for i in str2:
    print(i)
    print(str2.index(i))
    if i == '(':
        str1.replace(i, '')
#     for str1.index(i) in str1:
#         print(str1[str1.index(i)])
str2


# In[61]:


a = ''
if not a:
    print('rw')


# In[ ]:


'''
if empty, return
for i in s:
    if i == (:
        for i+1 in s:
            if i+1 ==):
                

'''


# In[ ]:


'''
idx = []
outter = 0
if empty, return

for i in s:
    if i == '(':
        if otter == 0:
            idx
            
        else:
            

'''


# In[57]:


def rmm(s):
    outter = 0
    x = ''
    
    for i in s:
        if i == '(' and outter > 0:
            x += i
            outter += 1
        if i == ')' and outter > 1:
            x += i
            outter -= 1
        outter += 1 if i == '(' else -1
            
            
    return x
            


# In[58]:


s = '()(())'
xx = rmm(s)
xx


# In[23]:


def rmp(s):
    idx = []
    outter = 0
    
    x = ''
    
    else:
        for i in s:
            if i == '(':
                if outter > 0:
                    idx.append(i)
                else:
                    idx.append(0)
                outter += 1
                
            else:
                if outter == 1:
                    idx.append(1)
                else:
                    idx.append(0)
                outter -= 1
    rmd = ''           
    for i in idx:
        if 
        
    return idx
                


# In[24]:


s = '()(())'


# In[30]:


b = rmp(s)
b


# In[32]:


[x if x == 1 for x in b]


# In[ ]:


rst = rmp(s)
rst

