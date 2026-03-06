"""
157.1299. Replace Elements with Greatest Element on Right Side
将每个元素替换为右侧最大元素

Given an array arr, replace every element in that array with the greatest element 
among the elements to its right, and replace the last element with -1.

After doing so, return the array.

 

Example 1:

Input: arr = [17,18,5,4,6,1]
Output: [18,6,6,6,1,-1]
 

Constraints:

1 <= arr.length <= 10^4
1 <= arr[i] <= 10^5


"""


def replaceElements(self, A, mx = -1):
    for i in xrange(len(A) - 1, -1, -1):
        A[i], mx = mx, max(mx, A[i])
    return A



def replaceElements(self, arr: List[int]) -> List[int]:
    mx = -1
    for i in range(len(arr) - 1, -1, -1):
        arr[i], mx = mx, max(arr[i], mx)
    return arr



def replaceElements(self, arr):
    me,arr[-1] = arr[-1],-1
    for i in range(len(arr)-2,-1,-1):
        arr[i],me = me,max(me,arr[i])
    return arr



def replaceElements(self, arr):
    rmax = arr[-1]
    for i in range(len(arr)-1,0,-1):
        temp = arr[i]
        arr[i] = rmax
        rmax = max(rmax, temp)
    arr[0] = rmax
    arr[-1]= -1
    return arr




def replaceElements(self, arr: List[int]) -> List[int]:
    m = -1
    i = len(arr) -1 
    while i >= 0:
        temp = arr[i]
        arr[i] = m
        if temp > m:
            m = temp
        i-= 1
    return arr


def replaceElements(self, arr: List[int]) -> List[int]:
    out = [-1]
    greatest = 0
    for num in arr[::-1]:
        if greatest < num:
            greatest = num
        out.append(greatest)
    out.pop()
    return out[::-1]



def replaceElements(self, arr: List[int]) -> List[int]:
    n = len(arr)
    ans = [0] * (n - 1) + [-1]
    for i in range(n - 2, -1, -1):
        ans[i] = max(ans[i + 1], arr[i + 1])
    return ans


def replaceElements(self, arr: List[int]) -> List[int]:
    res = [-1] * len(arr)
    for i in range(len(arr)-2, -1, -1):
        res[i] = max(arr[i+1], res[i+1])
    return res


def replaceElements(self, arr: List[int]) -> List[int]:
    res = [1]
    for i in range(len(arr)-1):
        res.append(max(arr[i+1:]))
    res.append(-1)
    return res










































































