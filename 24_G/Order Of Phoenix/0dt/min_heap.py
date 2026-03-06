

# Python3 implementation of Min Heap

import sys

class MinHeap:

	def __init__(self, maxsize):
		self.maxsize = maxsize
		self.size = 0
		self.Heap = [0]*(self.maxsize + 1)
		self.Heap[0] = -1 * sys.maxsize
		self.FRONT = 1

	# Function to return the position of
	# parent for the node currently
	# at pos
	def parent(self, pos):
		return pos//2

	# Function to return the position of
	# the left child for the node currently
	# at pos
	def leftChild(self, pos):
		return 2 * pos

	# Function to return the position of
	# the right child for the node currently
	# at pos
	def rightChild(self, pos):
		return (2 * pos) + 1

	# Function that returns true if the passed
	# node is a leaf node
	def isLeaf(self, pos):
		if pos >= (self.size//2) and pos <= self.size:
			return True
		return False

	# Function to swap two nodes of the heap
	def swap(self, fpos, spos):
		self.Heap[fpos], self.Heap[spos] = self.Heap[spos], self.Heap[fpos]

	# Function to heapify the node at pos
	def minHeapify(self, pos):

		# If the node is a non-leaf node and greater
		# than any of its child
		if not self.isLeaf(pos):
			if (self.Heap[pos] > self.Heap[self.leftChild(pos)] or
			self.Heap[pos] > self.Heap[self.rightChild(pos)]):

				# Swap with the left child and heapify
				# the left child
				if self.Heap[self.leftChild(pos)] < self.Heap[self.rightChild(pos)]:
					self.swap(pos, self.leftChild(pos))
					self.minHeapify(self.leftChild(pos))

				# Swap with the right child and heapify
				# the right child
				else:
					self.swap(pos, self.rightChild(pos))
					self.minHeapify(self.rightChild(pos))

	# Function to insert a node into the heap
	def insert(self, element):
		if self.size >= self.maxsize :
			return
		self.size+= 1
		self.Heap[self.size] = element

		current = self.size

		while self.Heap[current] < self.Heap[self.parent(current)]:
			self.swap(current, self.parent(current))
			current = self.parent(current)

	# Function to print the contents of the heap
	def Print(self):
		for i in range(1, (self.size//2)+1):
			print(" PARENT : "+ str(self.Heap[i])+" LEFT CHILD : "+
								str(self.Heap[2 * i])+" RIGHT CHILD : "+
								str(self.Heap[2 * i + 1]))

	# Function to build the min heap using
	# the minHeapify function
	def minHeap(self):

		for pos in range(self.size//2, 0, -1):
			self.minHeapify(pos)

	# Function to remove and return the minimum
	# element from the heap
	def remove(self):

		popped = self.Heap[self.FRONT]
		self.Heap[self.FRONT] = self.Heap[self.size]
		self.size-= 1
		self.minHeapify(self.FRONT)
		return popped

# Driver Code
if __name__ == "__main__":
	
	print('The minHeap is ')
	minHeap = MinHeap(15)
	minHeap.insert(5)
	minHeap.insert(3)
	minHeap.insert(17)
	minHeap.insert(10)
	minHeap.insert(84)
	minHeap.insert(19)
	minHeap.insert(6)
	minHeap.insert(22)
	minHeap.insert(9)
	minHeap.minHeap()

	minHeap.Print()
	print("The Min val is " + str(minHeap.remove()))






"""
Min Heap Implementation in Python
"""
class MinHeap:
    def __init__(self):
        """
        On this implementation the heap list is initialized with a value
        """
        self.heap_list = [0]
        self.current_size = 0
 
    def sift_up(self, i):
        """
        Moves the value up in the tree to maintain the heap property.
        """
        # While the element is not the root or the left element
        while i // 2 > 0:
            # If the element is less than its parent swap the elements
            if self.heap_list[i] < self.heap_list[i // 2]:
                self.heap_list[i], self.heap_list[i // 2] = self.heap_list[i // 2], self.heap_list[i]
            # Move the index to the parent to keep the properties
            i = i // 2
 
    def insert(self, k):
        """
        Inserts a value into the heap
        """
        # Append the element to the heap
        self.heap_list.append(k)
        # Increase the size of the heap.
        self.current_size += 1
        # Move the element to its position from bottom to the top
        self.sift_up(self.current_size)
 
    def sift_down(self, i):
        # if the current node has at least one child
        while (i * 2) <= self.current_size:
            # Get the index of the min child of the current node
            mc = self.min_child(i)
            # Swap the values of the current element is greater than its min child
            if self.heap_list[i] > self.heap_list[mc]:
                self.heap_list[i], self.heap_list[mc] = self.heap_list[mc], self.heap_list[i]
            i = mc
 
    def min_child(self, i):
        # If the current node has only one child, return the index of the unique child
        if (i * 2)+1 > self.current_size:
            return i * 2
        else:
            # Herein the current node has two children
            # Return the index of the min child according to their values
            if self.heap_list[i*2] < self.heap_list[(i*2)+1]:
                return i * 2
            else:
                return (i * 2) + 1
 
    def delete_min(self):
        # Equal to 1 since the heap list was initialized with a value
        if len(self.heap_list) == 1:
            return 'Empty heap'
 
        # Get root of the heap (The min value of the heap)
        root = self.heap_list[1]
 
        # Move the last value of the heap to the root
        self.heap_list[1] = self.heap_list[self.current_size]
 
        # Pop the last value since a copy was set on the root
        *self.heap_list, _ = self.heap_list
 
        # Decrease the size of the heap
        self.current_size -= 1
 
        # Move down the root (value at index 1) to keep the heap property
        self.sift_down(1)
 
        # Return the min value of the heap
        return root
"""
Driver program
"""
# Same tree as above example.
my_heap = MinHeap()
my_heap.insert(5)
my_heap.insert(6)
my_heap.insert(7)
my_heap.insert(9)
my_heap.insert(13)
my_heap.insert(11)
my_heap.insert(10)

print(my_heap.delete_min()) # removing min node i.e 5 

 