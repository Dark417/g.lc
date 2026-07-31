"""
playground


"""

# b = [1, 2, 3]

# a = [3, 4, 1, 3, 4, 9]
#
# largest_i = a.index(max(a))
# largest = max(a)
# print(largest_i)
# print(largest)
#
# a.remove(largest)
# largest_2 = max(a)
# largest_i2 = a.index(max(a))
#
# print(largest_2)
# print(largest_i2)

# parts = [merge, left, right] = [], [], []
# print(parts)

# collections.defaultdict(list)
# collections.Counter
# list((a & b).elements())

# class M:
# 	def __init__(self, key, value):
# 		self.key = key
# 		self.value = value


# input0 = [1, 2, 3, 4]
# i = len(input0[2:]) # 2个

# input0 = [1, 2, 3, 4]
# length = len(input0)
# for j in range(length - 2, -1, -1):
#     # l-2 is a real start
#     # to the one previous of the -1, which is 0
#     #
#     print(j)
#
# ini = input0[:-2]
# # to one previous to the -2
#
# # ini1 = input0[]
# # print(ini1)
#
#
# i0 = {2, 3, 1, 0, 2, 5, 3}
#
# for i in i0:
#     print(i)
#
# a = "abc"
# # if "a" or "b" in s: #???
# # if "a" and "b" in a:
#     print("rua")


# 程序员面试金典


# import sys
# if __name__ == "__main__":
#
#     n = int(sys.stdin.readline().strip())
#     urls = [None] * n
#
#     for i in range(n):
#         line = sys.stdin.readline().strip()
#         urls[i] = line
#
#     print(urls)


# dic = {}
# dic["a"] = ["b"]
# dic["a"] += "c"
# print(dic)

# 4 50


#
# n = int(input().strip())
# x = n[0]
# y = n[1]
# print(x)
# print(y)
#
# a = "abc"
# b = a.replace(a[2], "")
# print(b)

# for key, value in test_dict.items():
#     print (key, value)

# int cash=1024-num;
# int num_64=cash/64;
# int num_16=cash%64/16;
# int num_4=cash%64%16/4;
# int num_1=cash%64%16%4;
# cout<<num_64+num_16+num_4+num_1<<endl;

# a = False
# b = False
# if a or b:
#     print('rua')


# a = "ab"
# b = a.split()[-1]
# print(a.split()[-1])
# # b = len(a.split(" ")[-1])
# print(b)


# for i in range(10):
#     print(i, ~i)


# a = ["t","h","e"," ","s","k","y"," ","i","s"," ","b","l","u","e"]

# b = "abc"
# print("".join(a))

# a = ["a", "b", "c"]
# print("a".join("b"))

# a = "abcdefg"
# r = "".join(a[0:2][::-1] + a[3:40])
# index out of bound ok

# a = ""

# a.join(["a" + "b"])
# print(a)

# num1 = 20 if someBoolValue else num1
# if someBoolValue: num1=20
# a = 6
# a += 5 if 2>1 else 3

# a = (1,2,3)
# print(sum(i for i in a))

# a = "1"
# b = "2"
# x, y = map(lambda x: int(x), (a,b))

# a = (1,2)
# b = a + (3,)
# print(b)

# a = ()
# a += ((1,3))
# print(a)
# only one ()

# if 2>1: print(2)
# else: print(1)

# a = "abc"
# print(" ".join(a + "r"))
# a b c r

# a = "abc"
# b = "abd"
# diff = set(a).difference(b)
# print("".join(a) + "".join(diff))

# a = 'ZENOVW'
# ''.join(sorted(a))
# a = 'ZENOVW'
# b = sorted(a)
# print(sorted(a)) #list

# for k, v in dic.items()
# for k in dic
# for k in dic.keys()
# for v in dic.values()

# text = "balloon"
# b,a,l,o,n = map(lambda x: text.count(x), ("balon")) #"balon"
# x = list(map(lambda x: text.count(x), ("balon")))
# print(b, a, l, o, n)

# a = [1]
# print(a[0:1])


# my_set = {*my_list}
# my_list = [*my_set]

# a = "bb"
# print(a[1:-1]) #empty


# a = "xzi"
# print(sorted(a))			#list
# print("".join(sorted(a)))	#string
# print(" ".join(sorted(a)))

# #generator
# i for i in dic.values()
# # list
# [i for i in dic.values()]
# [a] += [b]
# [a, b]

# dict.get(key[, default])
# s1 = "ges"
# s2 = "bha"
# l1,l2 = map(lambda x: "".join(sorted(x)), (s1, s2))
# print(s1)
# print(s2)
# print(sorted(s1))

# s3 = "2"
# s4 = "5"
# l3, l4 = map(int, (s3, s4))
# print(l3, l4)

# x = [2, 3]
# a = sum(1 for i in x if i >2)
# print(a)

# a = "a b"
# print(list(a))
# print([a])

# s = "abcd"
# l = list(s)
# for i in l[::-1]:
# 	print(i)

# for i in range(len(l)-1, -1, -1):
# 	print(i)
# 3 2 1 0

# for index, i in enumerate(l[::-1]):
# 	# print(index, i)
# 	print(len(l)-1-index, i)
# 0 d
# 1 c
# 2 b
# 3 a

# 3 d
# 2 c
# 1 b
# 0 a

# l = [None]		#not a number
# l = [1, 2]
# l.append(3) if 0 else l.append(4)
# print(l)

# l = [[] for i in range(1, n)]

# l = [""* 4]		#1 list
# l = [""] * 4	#4
# l = [[]] * 4	#4
# print(l)

# a = []
# print(a += 4)

# queue.insert(len(queue), cur_v)

# call by reference
# def changeme( mylist ):
# 	print(id(mylist))
# 	mylist += [1,2,3,4]; # This would assig new reference in mylist
# 	print ("Values inside the function: ", mylist)
# 	print(id(mylist))
# 	return
# # Now you can call changeme function
# mylist = [10,20,30];
# print(id(mylist))
# changeme( mylist );
# print ("Values outside the function: ", mylist)
# print(id(mylist))

# https://stackoverflow.com/questions/986006/how-do-i-pass-a-variable-by-reference


# def foo(x, y):
#    x,y = x**2, y**2

# a = 2
# b = 3
# foo(a, b)  # a == 4; b == 9
# print(a, b)

# import copy

# a = [1, 2]
# b = copy.copy(a)
# c = a
# b.append(3)
# c[1] = 3
# print(a)
# print(b)
# print(c)


# copy deepcopy
# https://www.geeksforgeeks.org/copy-python-deep-copy-shallow-copy/
# import copy

# # initializing list 1
# li1 = [1, 2, [3,5], 4]
# # using copy to shallow copy
# li2 = copy.copy(li1)


# print(li1)
# print(li2)

# li2[2] = 7

# print(li1)
# print(li2)


# def r(l):
# 	#print(id(l))
# 	# new ref
# 	#b = [1,2,3]

# 	# new id
# 	#b = l.copy()

# 	# since new ref, doesn't change original
# 	b = l.copy()
# 	b[3] = [7,8]
# 	return b
# 	#print(id(b))

# a = [1,2,3, [5,6]]
# r(a)
# # print(id(b))
# print(a)
# # print(b)

# print(max(1 or 3))


# if fail: False, None, 0 and []

"""
x = None
if x:
	print ('if x' )
if x is not None:
	print ('if x is not None')

x = []
# x is not None

x = 42
if x:
	print ('if x' )
if x is not None:
	print ('if x is not None')
# both 1

class Foo(object):
	def __nonzero__(self):
		print ('Foo is evaluated to a boolean!')
		return True

x = Foo()
if x:
	print ('if x' )
if x is not None:
	print ('if x is not None')

# Foo is evaluated to a boolean!
# if x
# if x is not None

"""

# print(2 or 1)	2
# print(1 or 2)	1

# stack=[None]	#None
# stack=[()]		#[()]
# while stack:
# 	print(stack)


# for i in [1,None]:
# 	if i:
# 		print(i)

# a = [None]

# a = None
# if a:
# 	print(a)	#[None]
# while a:
# 	print("rua")

# for i in a:
# 	if not i:
# 		print(i)	#None


# l = [1]
# l.append(2,3)
# print(l)


# eval

# a = [None, 1]
# while []:		# nothing
# 	for n in a:
# 		print(n)	# print None


# a = 3 if 2>1 else 0
# print(a)

# def a(x, y):
# 	print(x+y)

# a(2, 3 if 2>1 else 1)

# a = 1 and 2
# print(a)
# None/0 if first None/0, else second


# a = set("1")
# b = set("2")
# print(a.union(b))
# a = {"x"}
# b = {"y"}
# print(a.union("b"))		# b second
# print(a.union({"b"}))	# SAME
# a = set("1")
# b = {"2"}
# print(a.union(b))

# a = False
# if not a:
# 	print("rua")


# a = [1,2,3]
# b = [4]
# b.append(a[:]) #shallow copy

# print(b)


# yield
# https://www.geeksforgeeks.org/difference-between-yield-and-return-in-python/?ref=rp

#*L will spread out the elements in L, so if L = [1,3,4,5], *L would be 1 3 4 5.


# a = [1]
# b = [2]
# c = [3]
# a.extend([b+c])
# a.extend([b, c])
# print(a)


# a = [[]]
# a.extend(1)		#err
# a.extend([1])		#[[], 1]	extend with list
# print(a)

# a = [1]
# b = a + [2]
# print(b)

# a = [12]
# b = [2]
# c = list(a+b)
# d = [3,2,1]
# d.sort()		# in line func first, then print itself
# print(d)


# a = ['i', 12, 'i', 'z', 4, 'n', 5]
# print(sum([i if str(i).isdigit() else 1 for i in a]))

# a = 1
# print(type(a) is int)  # is / ==

# print(len(" "))


# a = [1,2,3]
# a.reverse()
# print(a)	# in place first, then print / doesn't return
# print([i for i in reversed(a)])	# iterator

# a = [1,2,3,4]
# for i in range(len(a)-1, -1, -1):
# 	print(a[i])


# [] can't append
# path = []
# path +=[1]
# print(path)


# print("01" > "00")
# print("-" > "z")

# print(str(["a", "b"]))


# print([1] + [2])


# string.ascii_lowercase
# print(ord("a"))		#97

# print(chr(ord('z') + 1) == str(chr(ord('z') + 1)) )
# chr = str

# def a():
# 	return True
# print(1 == a())

# res = chr(96)
# print(res > "a")

# a = [1]
# print(a[0:5])

# print("azzzz" > "b")


# print(156>>1)

# print(range(1,100))


# n = 3
# while n:		# stop at 0
# 	print(n)
# 	n -= 1

# k = 0
# if not k: print("rua")

# if not 4%2:
# 	print("r")


# for i in range(0, 4, 2):
# 	print(i)

# print(5//2)


# def fac(n):
#     if n == 1: return n
#     return n* fac(n-1)

# def fac1(n):
# 	i = 1
# 	pdt = 1
# 	while i<=n:
# 		pdt *= i
# 		i += 1
# 	return pdt

# def fac2(n, i=1):
# 	if i > n: return 1
# 	if i <= n:
# 		return i*fac2(n, i+1)
# print(fac2(3))


# a = [1,2,3,4]
# v = [i for i in a if i >1]
# #x = [i if i >1 for i in a]	# err
# y = [i if i > 1 else 0 for i in a]
# print(v)
# #print(x)
# print(y)


# import math
# print(int(math.log10(100)))


# a = [1,2,3,4]
# for i in range(len(a)-1, -1, -1):
# 	print(i)


# /=
# //=


# a = [1,2,3,4,5,6,6]
# print(a[~2])
# print(~2)


# a = 1
# print(-a)


# for i in range(1, 2):
# 	print(i)


# print(int(1e9))


# a = 1
# b = 2
# # a, b = b, 3	# 2, 3
# # b, a = 3, b
# print(a, b)		# 2, 3


# nums1 = [1,2,3,0,0,0]
# l = []
# l[:] = nums1

# nums1[1] = 100
# print(l)


# a = [[]] * 3
# b = [[]* 3] 	# same

# a = [[7,0], [4,4], [7,1], [5,0], [6,1], [5,2]]
# # a.sort(reverse = True, key = lambda x: x[0])
# # a.sort(key = lambda x, y: x[1], y[1] if x[0] == y[0])
# for i in range(5):
# 	print(a.pop(1))

# a = [0] * 5
# print(a)

# print(max(0, None))	# err


# m = 3
# n = 2
# dp = [[1] * m for _ in range(n)]
# print(dp)


# path = [[1]*n for _ in range(m)]
# print(path)


# sys.maxsize
# import sys
# print(sys.maxsize)
# a = [1]
# print(a[11:])


# a = {1}
# print(type(a))

# print(1.0 is 1)


# a = {1, 2}
# b = {2, 3}
# print(a^b)
# print(b^a)


# print(98^97)


# def rec(s):
# 	print(s)
# 	if len(s) < 3:
# 		return "".join(s)
# 	if len(s) == 3:
# 		if s[0] == s[1] == s[2]:
# 			return "".join(s[:2])
# 		else:
# 			return "".join(s)
# 	if len(s) > 3:
# 		if s[0] == s[1] == s[2]:
# 			return s[:2] + rec(s[3:])
# 		if s[0] == s[1] and s[2] == s[3]:
# 			return "".join(s[0:3]) + rec(s[4:])
# 		else:
# 			return s[0] + rec(s[1:])


# n = int(input())
# for _ in range(n):
# 	l = list(input())
# 	s = ""
# 	print(rec(l))


# while True:
#     l = input()
#     if l:
#         print(l)
#         # print(l.split(")")[1])
#         # l = input().strip()
#     else:
#         break


#

# get an element from set
# next(iter(s1))


# a = {1, 2}
# b = {1, 2, 3}
# print(a < b)
# print(a.issubset(b))


# a = {'g': [1, 2], 'x': [3, 4], 'z': [5,6]}
# for x in a:
#     print(reduce(lambda x,y: x+y, a[x]))
# import collections
# que = collections.deque([("x", 1)])
# x = collections.deque(("x", 1))
# for i in que:
#     	print(i)
# for i in x:
#     	print(i)

# x = []
# while True:
#     t = input().split()

#     x.append(t)
#     print(x)




# a = 5
# b = 3
# l = [[0] * b for i in range(a)]


# #reverse a string
# s[::-1]
# [len(s)::-1]
# s = ''.join(reversed(s))

# def reverse(s): 
#   str = "" 
#   for i in s: 
#     str = i + str
#   return str

# def reverse(s): 
#     if len(s) == 0: 
#         return s 
#     else: 
#         return reverse(s[1:]) + s[0] 


# len(n)/2 returns 3.0
# return -1
# xrange(1, 4)


# l = [1, 2, 3, 1]
# for i in l:
#     print(l.index(i))

# range(1, 5)


# a = [[1, 22], [2, 3], [3, 4]]
# a.sort(key=lambda r: r[1])
# vertices = set(list(i[0] for i in w_list))

# dict.keys()




# l = [1, 2, 3]
# >>> print(' '.join(str(x) for x in l))
# 1 2 3
# >>> print(' '.join(map(str, l)))
# 1 2 3


# a = [1, 2, 3, 4, 5]
# print(*a, sep = ',')

# a = [1, 2, 3]
# print(a[1.5])
# print([1] + 3)

# def a():
#     x = [1, 2, 3]
# 	return (i for i in x if i > 1)

# print(a())

# i = 5
# print([i] * 10)
# print([i * 10])


# res = ["" ]* 3 * 4
# print(res)

# import itertools

# num = [1, 1,2 ,4]


# print(int(num[:3] or "0"))

# a = []
# print(a[-1])

# a = ""
# if a:
#     print("rua")
# else:
#     print("wf")



a = [1, 2]

print( all(i in a for i in range(1, 3)))

a = [1,2,3, 5, 7]


for i in range(len(a)):
	print(i)



#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

#
#
#
#
#

#
#
#
#
#

#
#
#
#
#

#
#
#
#
#
