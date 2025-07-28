"""
977. Squares of a Sorted Array

Given an array of integers A sorted in non - decreasing order, return an array of the
squares of each number, also in sorted non - decreasing order.

Example
1:

Input: [-4, -1, 0, 3, 10]
Output: [0, 1, 9, 16, 100]
Example
2:

Input: [-7, -3, 2, 3, 11]
Output: [4, 9, 9, 49, 121]

Note:
1 <= A.length <= 10000
-10000 <= A[i] <= 10000
A is sorted in non - decreasing
order.

!
for i in list:
    <0 -> list1
    >=0 -> list2
merge
    while list
"""

input0 = [-4, -1, 0, 3, 10]
input1 = [-7, -3, 2, 3, 11]

# 10-line
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


def sortedSquares(self, A):
    l, r, answer = 0, len(A) - 1, [0] * len(A)
    while l <= r:
        left, right = abs(A[l]), abs(A[r])
        answer[r - l] = max(left, right) ** 2
        l, r = l + (left > right), r - (left <= right)
    return answer


def sortedSquares(self, A: 'List[int]') -> 'List[int]':
    answer = [] # list
    l, r = 0, len(A) - 1
    while l <= r:
        left, right = abs(A[l]), abs(A[r])
        if left > right:
            answer.append(left * left)
            l += 1
        else:
            answer.append(right * right)
            r -= 1
    return (answer[::-1]) # reverse list using step of -1 [::-1]


# official solution
def sortedSquares(self, A: List[int]) -> List[int]:
    N = len(A)
    # i, j: negative, positive parts
    j = 0
    while j < N and A[j] < 0:
        j += 1
    i = j - 1

    ans = []
    while 0 <= i and j < N:
        if A[i] ** 2 < A[j] ** 2:
            ans.append(A[i] ** 2)
            i -= 1
        else:
            ans.append(A[j] ** 2)
            j += 1

    while i >= 0:
        ans.append(A[i] ** 2)
        i -= 1
    while j < N:
        ans.append(A[j] ** 2)
        j += 1

    return ans



def sqr_of_array(list):
    sqr1 = []
    sqr2 = []
    result = []
    for i in list:
        if i <= 0:
            sqr1.insert(0, i*i)
        else:
            sqr2.append(i*i)

    i = 0
    j = 0

    while i < len(sqr1) and j < len(sqr2):
        if sqr1[i] <= sqr2[j]:
            result.append(sqr1[i])
            i += 1
        else:
            result.append(sqr2[j])
            j += 1

    if i < len(sqr1):
        for i in sqr1[i:]:
            result.append(i)
    elif j < len(sqr2):
        for i in sqr2[j:]:
            result.append(i)

    return result

result = sqr_of_array(input1)
print(result)


