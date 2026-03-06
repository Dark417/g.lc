
###################################################
# Chapter 1: Abstract Data Types
"""
p7 calendar
p 11 


ADT
design
implement an ADT

implement an known data structure


define a class
	self
	functions

precondition / postcondition

1.3 Bag
p16
p19

p21 iterator
p22 for iterator


"""
# Implements the Bag ADT container using a Python list.
class Bag :
# Constructs an empty bag.
def __init__( self ): self._theItems = list()
# Returns the number of items in the bag.
def __len__( self ):
return len( self._theItems )
# Determines if an item is contained in the bag.
def __contains__( self, item ): return item in self._theItems
# Adds a new item to the bag.
def add( self, item ): self._theItems.append( item )
# Removes and returns an instance of the item from the bag.
def remove( self, item ):
assert item in self._theItems, "The item must be in the bag." ndx = self._theItems.index( item )
return self._theItems.pop( ndx )
# Returns an iterator for traversing the list of items.
def __iter__( self, item ): ......




###################################################
# Chapter2: Arrays



"""
compile to executable
The ctypes Module

iterator


"""


# 2.2 The Python List

"""
length
capacity
array

append expand
extend
insert
remove
	pop
slice

"""

pyList = [ 4, 12, 2, 34, 17 ]
pyList.append( 50 )




pyList.insert( 3, 79 )

pyList.pop( 0 ) # remove the first item 
pyList.pop() # remove the last item

aSlice = theVector[2:3]




# 2.3 Two-Dimensional Arrays
"""

Array2D( nrows, ncols )
numRows()
numCols()
clear( value )
getitem( i1, i2 )
setitem(i1, i2, value)

xr,c
x[r][c] or x[r,c]



"""




# 2d Array
# Implementation of the Array2D ADT using an array of arrays.




# 2.4 The Matrix Abstract Data Type
"""
Matrix( rows, ncols )
numRows()
numCols()
􏰁getitem ( row, col )
􏰁setitem ( row, col, scalar )
􏰁scaleBy( scalar )
transpose()
add ( rhsMatrix ): Creates and returns a new matrix that is the result of adding this matrix to the given rhsMatrix. The size of the two matrices must be the same.
􏰁
subtract ( rhsMatrix ): The same as the add() operation but subtracts the two matrices.
􏰁multiply ( rhsMatrix ): Creates and returns a new matrix that is the result of multiplying this matrix to the given rhsMatrix. The two matrices must be of appropriate sizes as defined for matrix multiplication.

"""




###################################################
# Chapter 3: Set and Maps
"""
p70 set

p73 set class


p77 map
p78 map class
p86 *args
*args as tuple 

p89 multiarray

p116 sparsematrix


!! 117 4.5.1



"""



###################################################
# Chapter 4: Algorithm Analysis
"""
p113 set analysis




"""


###################################################
# Chapter 5: Searching and Sorting
"""
Searching
p127 linearSearch
128 search sorted list
    min()

130 binarySearch

Sorting
134 bubble sort
137 selection sort
140 insertion sort
143 find position()
146 merge sorted list

148 - ... set
152 sorted comp




"""



###################################################
# Chapter 6: Linked Structures
"""
156 node
161 node traversal

162 prepending node
165 remove node

166 bag linked list
168 linked list iterator

170 ll append
171 ll remove
172 ll sorted linear search
    ll inserting node



"""



###################################################
# Chapter 7: Stack
"""
194 stack def
196 stack list
197 stack linked list

202 balanced brackets

212 maze ADT




"""

###################################################
# Chapter 8: Queues
"""
222 queue def
223 list queue

227 array queue
229 linkedlist queue

230 priority queue
232 list
234 linked list
246 bounded priority queue

286 reverse linkedlist brute force
287 reverse ll stack
288 reverse ll recursive stack

291 recursive binary search

"""



###################################################
# Chapter 9: Advanced Linked Lists
"""
248 doubly ll
249 r traverse doubly ll
253 insert sorted dll
	exe

255 circular ll
256 search circular ll
257 insert
	exe remove


260 multi ll



"""





###################################################
# Chapter 10: Recursion

"""

286 A brute-force approach for printing a singly linked list in reverse order.
287 stack reverse linked list

294 Hanoi
296 exponential
297 recursive exp


"""






###################################################
# Chapter 12: Advanced Sorting

"""
341 merge sort
343 mergesort virtual sublist
343 merge VirtualSeq
	345 rec init tempArray

350 quick sort

357 radix sort

359 ll insertion sort

362 ll merge sort





"""




###################################################
# Chapter 13: Binary Tree

"""
376 binary tree node cls
378 preorder traversal
	inorder traversal
379 postorder travel
381 bfs travel


13.4 heap
396 heap class



"""






























