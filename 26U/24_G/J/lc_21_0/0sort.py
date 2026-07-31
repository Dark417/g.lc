
"""
merge-sort
	two / one function

	complicated while
	while i j + while i + while j

	old / new arr

quick-sort
	random / left / right partition
	pointer manipulation

heap-sort


bubble-sort
	with flag

insertion-sort
	binary-insertion-sort

selection-sort


radix-sort

counting-sort

bucket-sort



"""

# merge-sort
# new arr
def merge(A, B):
	l1, l2 = len(A), len(B)
	i = j = 0
	arr = []
	while i < l1 or j < l2:
		if i == l1 or (j < l2 and A[i] > B[j]):
			arr.append(B[j])
			j += 1
		else:
			arr.append(A[i])
			i += 1
	return arr

def merge(A, B):
	l1, l2 = len(A), len(B)
	i = j = 0
	arr = []
	while i < l1 and j < l2:
		if A[i] <= B[j]:
			arr.append(A[i])
			i += 1
		else:
			arr.append(B[j])
			j += 1
	while i < l1:
		arr.append(A[i])
		i += 1
	while j < l2:
		arr.append(B[j])
		j += 1
	return arr

def mergesort(arr):
	if len(arr) == 1:
		return arr
	mid = len(arr) // 2
	A = mergesort(arr[:mid])
	B = mergesort(arr[mid:])
	return merge(A, B)


# count inversion
def cross_count(B, C, n1, n2):
    count = 0
    A = []
    i = 0
    j = 0
    while i <= n1 - 1 or j <= n2 - 1:
        if j > n2 - 1 or (i <= n1 - 1 and B[i] <= C[j]):
            A.append(B[i])
            i += 1
            count += j
        else:
            A.append(C[j])
            j += 1
    return count, A

def merge_count(A, n):
    if n == 1:
        return 0, A
    c1, B = merge_count(A[:n // 2], n // 2)
    c2, C = merge_count(A[n // 2:], n - n // 2)
    c3, A = cross_count(B, C, n // 2, n - n // 2)
    count = c1 + c2 + c3

    return count, A



# change arr
def mergeSort(arr):
    if len(arr) > 1:
        mid = len(arr)//2
        L = arr[:mid]
        R = arr[mid:]
        mergeSort(L)
        mergeSort(R)
 
        i = j = k = 0
        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1
        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1
        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1

def merge_sort(nums, l, r):
    if l == r:
        return
    mid = (l + r) // 2
    merge_sort(nums, l, mid)
    merge_sort(nums, mid + 1, r)
    tmp = []
    i, j = l, mid + 1
    while i <= mid or j <= r:
        if i > mid or (j <= r and nums[j] < nums[i]):
            tmp.append(nums[j])
            j += 1
        else:
            tmp.append(nums[i])
            i += 1
    nums[l: r + 1] = tmp

def sortArray(nums: List[int]) -> List[int]:
    merge_sort(nums, 0, len(nums) - 1)
    return nums



# quick-sort
def partition(nums, l, r):
    pivot = random.randint(l, r)
    nums[pivot], nums[r] = nums[r], nums[pivot]
    i = l - 1	# i = l
    for j in range(l, r):
        if nums[j] < nums[r]:
            i += 1
            nums[j], nums[i] = nums[i], nums[j]
            # i += 1
    i += 1	# //rm
    nums[i], nums[r] = nums[r], nums[i]
    return i

def partition(self, nums, l, r):
    pivot = random.randint(l, r)
    nums[pivot], nums[l] = nums[l], nums[pivot]
    i = l 	#i = l + 1
    for j in range(l + 1, r + 1):
        if nums[j] < nums[l]:
        	# i += 1
            nums[j], nums[i] = nums[i], nums[j]
            i += 1
    nums[i], nums[l] = nums[l], nums[i]
    # nums[i - 1], nums[l] = nums[l], nums[i - 1]
    return i - 1


def quicksort(nums, l, r):
    if r - l <= 0:
        return
    mid = partision(nums, l, r)
    quicksort(nums, l, mid - 1)
    quicksort(nums, mid + 1, r)

def sortArray(nums: List[int]) -> List[int]:
    randomized_quicksort(nums, 0, len(nums) - 1)
    return nums



# heap-sort
def max_heapify(heap, root, heap_len):
    p = root
    while p * 2 + 1 < heap_len:
        l, r = p * 2 + 1, p * 2 + 2
        if heap_len <= r or heap[r] < heap[l]:
            nex = l
        else:
            nex = r
        if heap[p] < heap[nex]:
            heap[p], heap[nex] = heap[nex], heap[p]
            p = nex
        else:
            break
    
def build_heap(heap):
    for i in range(len(heap) - 1, -1, -1):
        max_heapify(heap, i, len(heap))

def heap_sort(nums):
    build_heap(nums)
    for i in range(len(nums) - 1, -1, -1):
        nums[i], nums[0] = nums[0], nums[i]
        max_heapify(nums, 0, i)
        
def sortArray(nums: List[int]) -> List[int]:
    heap_sort(nums)
    return nums




def heapify(arr, n, i):
    largest = i  # Initialize largest as root
    l = 2 * i + 1     # left = 2*i + 1
    r = 2 * i + 2     # right = 2*i + 2
    if l < n and arr[largest] < arr[l]:
        largest = l
    if r < n and arr[largest] < arr[r]:
        largest = r
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]  # swap
        heapify(arr, n, largest)
 
def heapSort(arr):
    n = len(arr)
    for i in range(n//2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n-1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]  # swap
        heapify(arr, i, 0)









# bubble-sort
def bubblesort(arr):
	n = len(arr)
	for i in range(n - 1):
		for j in range(n - i - 1):
			if arr[j] > arr[j + 1]:
				arr[j], arr[j + 1] = arr[j + 1], arr[j]
	return arr

# early stop
def bubble_sort(array):
    n = len(array)
    for i in range(n):
        already_sorted = True
		for j in range(n - i - 1):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
				already_sorted = False
		if already_sorted:
            break
    return array




# insertion-sort
def insertion_sort(array):
    for i in range(1, len(array)):
        key_item = array[i]
        j = i - 1
        while j >= 0 and array[j] > key_item:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = key_item
    return array


# binary-insertion-sort
def binary_search(arr, val, start, end):
    if start == end:
        if arr[start] > val:
            return start
        else:
            return start+1
    if start > end:
        return start
 
    mid = (start+end)/2
    if arr[mid] < val:
        return binary_search(arr, val, mid+1, end)
    elif arr[mid] > val:
        return binary_search(arr, val, start, mid-1)
    else:
        return mid

# some problem
# def binary_search(arr, val, low, high):
# 	if low == high:
# 		return low
# 	mid = low + (high - low) // 2
# 	if val < arr[mid]:
# 		return binary_search(arr, val, low, mid)
# 	elif val > arr[mid]:
# 		return binary_search(arr, val, mid + 1, high)
# 	else:
# 		return mid

def insertion_sort(arr):
    for i in range(1, len(arr)):
        val = arr[i]
        j = binary_search(arr, val, 0, i-1)
        # arr = arr[:j] + [val] + arr[j:i] + arr[i+1:]
        
        for k in range(i - 1, j - 1, - 1):
        	arr[k + 1] = arr[k]
        arr[j] = val
    return arr




# selection-sort
def selection_sort(arr):
    for i in range(len(arr)): 
    	min_idx = i 
	    for j in range(i+1, len(arr)): 
	        if arr[min_idx] > arr[j]: 
	            min_idx = j    
	    arr[i], arr[min_idx] = arr[min_idx], arr[i] 




# radix-sort












