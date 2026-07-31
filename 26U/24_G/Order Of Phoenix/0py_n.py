#this doc writes python lines

#!/usr/bin/env python
# coding: utf-8

###################################################################
#todo




###################################################################
#class

_var intended private
var_ avoid collision
__var avoid subclass name collision
__var__ python use



###################################################################
# function
def __init__( self ):


def returntuple():
    a = 4
    b = 5
    c = 8
    return a, b, c
print(returntuple())
#(a, b, c)


###################################################################
#scope
l = '123'
x = [1, 2, 3]
for i in range(len(l)):
    x[i] = [i for i in l]
print(x)

###################################################################
#datatypes
#list
.list()
#convert to list

#delete
clear() Remove all items: 
pop() Remove an item by index and get its value: 
remove() Remove an item by value: 
del() Remove items by index or slice: 
Remove multiple items that meet the condition: List comprehensions

list.pop()
#get the last one; remove it from the list

list.index(item)
list.reverse()
list.insert(index, var)
[::-1]
#return index


#
set()		#return a set, rm duplicates
range()

res = [None] * size #create an empty [] of len(size)



a = (i for i in b if i> 1)
a = (i > 1 for i in b)

###################################################################
#syntax
x = 1 if 2>1 else 0
x = x for x in y if x > 0

l
assert item in self._theItems, "The item must be in the bag."



###################################################################
#common funcs
print()
dir(instance)
# print all attributes' names

id(obj)

a = ['red', 'yellow', 'orange']
print(a)
# ba = sorted(a)
b = a.sorted()
print(b)

b = ['grey', 'green', 'blue']
sb = sorted(b)
print(b)
print(sb)

a = [3,4,1]
c = a.sort()
c = sorted(a)

#map
map(func_, vars_)
map(lambda x: x + x, numbers)
map(lambda x, y: x + y, numbers1, numbers2)

l = ['sat', 'bat', 'cat', 'mat']
# map() can listify the list of strings individually
test = list(map(list, l))

###################################################################
#libs
random
array

ctypes
from array import Array








###################################################################




for i, j in enumerate(nums):
    print(i, j)




a = ["1","2","5"]
n1 = ord(a.pop())-ord('0')



#input domain, extreme cases

# basic operation
get_ipython().run_line_magic('', '')


k = None
if not k:
    print('rua')
if k is None:
    print('rua')

k = 0
if not k:
    print('rua')

if k is None:

c = 1
# check boolean
if c:
	print("yes")
if not c:
	print("yes")

c = 1
c = 0
if c is not None:
	print("yes")
# both yes

c = None
if c is None:
	print("yes")

c = 3
if c != 1:
	print('yes')

c = 3
if c is not 3:
	print('yes')


def g(y):
	print(x)
	print(x + 1)
x = 5
g(x)
print(x)

def h(y):
	print(x)
	x = x +1
x=5
h(x)
print(x)

a = (1,2,3)
for i in a:
	print(i)

a = 0
L = [1,2,3,4,5]
for i in range(len(L)):
	print(L[i])
	a += L[i]
print(a)

for i in range(5):
	print(i)
# 0 1 2 3 4

a = [10, 2, 3, 4, 5]

#print index
print(*range(1, len(a)))

list = [*range(a[0], a[-1]), a[-1]]
print (list)

for i in a:
	print(a.index(i))


for x in [range(a[0], a[len(a)-1])]:
	print(x)

print(i for i in range(5))


print(range(2, len(a), 1))
b = [range(2, len(a))]

for i in [range(2, len(a))]:
	print(a[i])

for i in range(len(a)):
	print(a[i])
for i in range(len(a), 7):
	print(i)



c = '123'
if '12' in c:
	print( 'true' )


def mult(a, b):
	result = 0
	while b > 0:
		result += a
		b -= 1

	return result

x = mult(1,2)
print(x)

a = [1,2]
b = (1,2)

d = (1, (2,3))
print(d)

a = [1,2,3]
if b is not None:
	print('None')

d = {}
for i in xrange(4000000):
	d[i] = None


assert element in self, "The element must be in the set."


fun( *args):
	# many...args

def Set( self, *initElements = None)



import bisect 
a = [1, 2, 4, 5] 
bisect.insort(a, 3) 










import collections

# a = 1
# if a:
# 1 a True
# 1 not a False
# 0 not a True
# 0 a False

# a = -1
# if a:
# 	print("rua")


# a = "x"
# a += "y"	# "xy"
# a = "z" + a
# print(a)


# print(11/10)


A = [1,2,0,0]
print(list(map(str, A)))



import math
print(int(math.log10(101)))
print(math.floor(math.log10(101)))


someddict = collections.defaultdict(list)
print(someddict[3])



value = d.get(key, "empty")



x = [1, 2, 3, 4]
print(list(i for i in x if i > 1 ))
print(list(i if i > 1 else 0 for i in x))













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

res = sorted(d.items(), key=lambda x: x[1])
res = sorted(d.items(), key=lambda x: x[1], reverse=True)
sorted_dict = dict(sorted(d.items(), key=lambda x: x[1], reverse=True))
res = sorted(cnt.items(), key=lambda x: x[1], reverse=True)




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




























































