###############################################################
"""



legitimate init
access


running time


python fundamentals

id()	get address

list
set
dictionary

collection
	q

pop
delete





assert

function
	*args

	pack, unpack



class
	inner function


	




libraries
	path
	array
	random


import bisect 
a = [1, 2, 4, 5] 
bisect.insort(a, 3) 


	
cls
func


datatypes
int
    float
        sci num
str
list
tuple
dict
https://realpython.com/iterate-through-dictionary-python/



conditions



iterations



libs




"""












###############################################################
# conditions
"""


"""
if not x in iter:
if x not in iter:
if not s: return 0


###############################################################
# libs
"""
random
math
re
collections


"""








###############################################################
# class

class Solution(object):
    _dp = [0]
    def numSquares(self, n):
        dp = self._dp


class Solution(object):

    def __init__(self, x):
    	self.dp = x

    def numSquares(self, n):
        dp = self._dp






###############################################################
###############################################################

# function








# return
# one line
a = [1,2,3,4]
v = [i for i in a if i >1]
#x = [i if i >1 for i in a]	# err
y = [i if i > 1 else 0 for i in a]











###############################################################
# for, while



# for else
# when for completes: else; if break, then break out
for i in a:
	if i == 2:
		break
	print(i)
else:
	print("rua")






###############################################################
###############################################################
# datatypes




###############################################################
# assignment
a, b = b, a

a, b = 1, 3
a, b = max(a,b), min(a+1, b)

#同时发生


#The comma actually changes the assignment value to be a tuple (iterable) and therefore extends the array
res += num, 
res+= [num]



###############################################################
# OP

# int



# logic
a *= b or 1



# bit
~n = -n - 1
x ^ y
# y 0, x = x	y 1, x complement






# div
n, digit = divmod(n, 10)





###############################################################
# chr / str
ord()

















###############################################################
# list

# funcs
reversed(row)

# sort in-place
l.sort(key = lambda x: x[0])
a.sort(key = lambda x: (x[0], x[1]))
a.sort(key = lambda x: (-x[0], x[1]))



# new
sorted(l)

# slicing
nums1 = [1,2,3,0,0,0]
nums1 = nums1[:3]
l = nums1

l = []
l[:] = nums1
l = nums1.copy()

a = []
a[:-1]



sum([])		# 0
sum([],[])	# []



# map
aux_list = map(lambda x: (sorting_criterion_1(x),
                          sorting_criterion_2(x),
							x), star_list)

# filter

# reduce
def reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        value = next(it)
    else:
        value = initializer
    for element in it:
        value = function(value, element)
    return value



zip(a, b)
# only zip min(len(a), len(b)) number

result = zip(coordinate, value)
list(result)

# unzip
c, v =  zip(*result_list)


[*map(s.index, s)] == [*map(t.index, t)]
* to unzip iterator


###############################################################
# dictionary




dict.clear()
#Removes all elements of dictionary dict

dict.copy()
#Returns a shallow copy of dictionary dict

dict.fromkeys()
#Create a new dictionary with keys from seq and values set to value.

dict.get(key, default=None)
#For key key, returns value or default if key not in dictionary

dict.has_key(key)
#Returns true if key in dictionary dict, false otherwise

dict.items()
#Returns a list of dict's (key, value) tuple pairs

dict.keys()
#Returns list of dictionary dict's keys

dict.setdefault(key, default=None)
#Similar to get(), but will set dict[key]=default if key is not already in dict

dict.update(dict2)
#Adds dictionary dict2's key-values pairs to dict

dict.values()
#Returns list of dictionary dict's values



sum(c.values())                 # total of all counts
c.clear()                       # reset all counts
list(c)                         # list unique elements
set(c)                          # convert to a set
dict(c)                         # convert to a regular dictionary
c.items()                       # convert to a list of (elem, cnt) pairs
Counter(dict(list_of_pairs))    # convert from a list of (elem, cnt) pairs
c.most_common()[:-n-1:-1]       # n least common elements
c += Counter()                  # remove zero and negative counts


counter.most_common(1)[0][1]

a = Counter()
a['a'] += 1  # 直接+ 

###############################################################


















































