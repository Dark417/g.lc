"""
179.977. Squares of a Sorted Array
有序数组的平方


Given an array of integers A sorted in non-decreasing order, return an array of the 
squares of each number, also in sorted non-decreasing order.

 

Example 1:

Input: [-4,-1,0,3,10]
Output: [0,1,9,16,100]
Example 2:

Input: [-7,-3,2,3,11]
Output: [4,9,9,49,121]
 

Note:

1 <= A.length <= 10000
-10000 <= A[i] <= 10000
A is sorted in non-decreasing order.
"""


def sortedSquares(self, A: List[int]) -> List[int]:
    return sorted([i*i for i in A])


def sortedSquares(self, A: List[int]) -> List[int]:
    for i in range(len(A)):
        A[i] *= A[i]
    A.sort()
    return A


def sortedSquares(self, A: List[int]) -> List[int]:
    return_array = [v**2 for v in A]
	return_array.sort() # This is in place!
	return return_array


def sortedSquares(self, nums: List[int]) -> List[int]:
    n = len(nums) - 1
    i, j = 0, n
    arr = [0] * (n + 1)
    while i <= j:
        if abs(nums[i]) >= abs(nums[j]):
            arr[n] = nums[i] * nums[i]
            i += 1
        else:
            arr[n] = nums[j] * nums[j]
            j -= 1
        n -= 1
    return arr

        

def sortedSquares(self, A):
    N = len(A)
    # i, j: negative, positive parts
    j = 0
    while j < N and A[j] < 0:
        j += 1
    i = j - 1

    ans = []
    while 0 <= i and j < N:
        if A[i]**2 < A[j]**2:
            ans.append(A[i]**2)
            i -= 1
        else:
            ans.append(A[j]**2)
            j += 1

    while i >= 0:
        ans.append(A[i]**2)
        i -= 1
    while j < N:
        ans.append(A[j]**2)
        j += 1

    return ans



def sortedSquares(self, A: List[int]) -> List[int]:
	answer = collections.deque()
    l, r = 0, len(A) - 1
    while l <= r:
        left, right = abs(A[l]), abs(A[r])
        if left > right:
            answer.appendleft(left * left)
            l += 1
        else:
            answer.appendleft(right * right)
            r -= 1
    return list(answer)



def sortedSquares(self, A):
    answer = [0] * len(A)
    l, r = 0, len(A) - 1
    while l <= r:
        left, right = abs(A[l]), abs(A[r])
        if left > right:
            answer[r - l] = left * left
            l += 1
        else:
            answer[r - l] = right * right
            r -= 1
    return answer


# nice a xd
def sortedSquares(self, A):
    l, r, answer = 0, len(A) - 1, [0] * len(A)
    while l <= r:
        left, right = abs(A[l]), abs(A[r])
        answer[r - l] = max(left, right) ** 2
        l, r = l + (left > right), r - (left <= right)
    return answer











































































