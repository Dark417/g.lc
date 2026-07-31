"""
202.905. Sort Array By Parity
按奇偶排序数组

Given an array A of non-negative integers, return an array consisting of all the even 
elements of A, followed by all the odd elements of A.

You may return any answer array that satisfies this condition.

 

Example 1:

Input: [3,1,2,4]
Output: [2,4,3,1]
The outputs [4,2,3,1], [2,4,1,3], and [4,2,1,3] would also be accepted.
 

Note:

1 <= A.length <= 5000
0 <= A[i] <= 5000

"""


def sortArrayByParity(self, A):
    A.sort(key = lambda x: x % 2)
    return A



def sortArrayByParity(self, A):
    return ([x for x in A if x % 2 == 0] + 
            [x for x in A if x % 2 == 1])


def sortArrayByParity(self, A):
	i, j, l = 0, len(A)-1, [0]*len(A)
	for k in range(len(A)):
		if A[k] % 2:
			l[j] = A[k]
			j -= 1
		else:
			l[i] = A[k]
			i += 1
	return l

		


def sortArrayByParity(self, A):
    i, j = 0, len(A) - 1
    while i < j:
        if A[i] % 2 > A[j] % 2:
            A[i], A[j] = A[j], A[i]

        if A[i] % 2 == 0: i += 1
        if A[j] % 2 == 1: j -= 1

    return A



def sortArrayByParity(self, A: List[int]) -> List[int]:
    i = 0
    for j in range(len(A)):
        if A[j] % 2 == 0:
            A[i], A[j] = A[j], A[i]
            i += 1
    return A


def sortArrayByParity(self, A: List[int]) -> List[int]:
    i, j = 0, len(A) - 1
    while i < j:
    	if A[i] % 2 == 1 and A[j] % 2 == 0: A[i], A[j] = A[j], A[i]
    	i, j = i + 1 - A[i] % 2, j - A[j] % 2
    return A


















































































