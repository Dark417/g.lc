"""
156.1502. Can Make Arithmetic Progression From Sequence
判断能否形成等差数列


Given an array of numbers arr. A sequence of numbers is called an arithmetic 
progression if the difference between any two consecutive elements is the same.

Return true if the array can be rearranged to form an arithmetic progression, otherwise, return false.

 

Example 1:

Input: arr = [3,5,1]
Output: true
Explanation: We can reorder the elements as [1,3,5] or [5,3,1] with differences 2 
and -2 respectively, between each consecutive elements.
Example 2:

Input: arr = [1,2,4]
Output: false
Explanation: There is no way to reorder the elements to obtain an arithmetic progression.
 

Constraints:

2 <= arr.length <= 1000
-10^6 <= arr[i] <= 10^6



"""

def canMakeArithmeticProgression(self, arr: List[int]) -> bool:
    m = min(arr)
    gap = (max(arr) - m) / (len(arr) - 1)
    if gap == 0: return True
    s = set(num - m for num in arr)
    return len(s) == len(arr) and all(diff % gap == 0 for diff in s)


def canMakeArithmeticProgression(self, arr: List[int]) -> bool:
    m = min(arr)
    gap = (max(arr) - m) / (len(arr) - 1)
    if gap == 0: return True
    i = 0
    while i < len(arr):
        if arr[i] == m + i * gap:
            i += 1
        else:
            dis = arr[i] - m
            if dis % gap != 0: return False
            pos = int(dis / gap)
            if arr[pos] == arr[i]: return False
            arr[pos], arr[i] = arr[i], arr[pos]
    return True

arr.sort()
return len(set(arr[i-1] - arr[i] for i in range(1, len(arr)))) == 1

return len(set(sorted(arr)[i-1] - sorted(arr)[i] for i in range(1, len(arr)))) == 1


def canMakeArithmeticProgression(self, arr: List[int]) -> bool:
    arr.sort()
    for i in range(1, len(arr)-1):
        if arr[i] - arr[i-1] != arr[i+1]-arr[i]:
            return False
    return True



def canMakeArithmeticProgression(self, arr: List[int]) -> bool:
    arr.sort()
    a=[arr[i+1]-arr[i] for i in range(len(arr)-1)]
    if len(set(a))==1:
        return True
    else:
        return False


def canMakeArithmeticProgression(self, arr: List[int]) -> bool:
    arr.sort()
    for i in range(1, len(arr) - 1):
        if arr[i] * 2 != arr[i - 1] + arr[i + 1]:
            return False
    return True






def canMakeArithmeticProgression(self, arr: List[int]) -> bool:
    arr.sort()
    for i in range(1, len(arr) - 1):
        if arr[i] * 2 != arr[i - 1] + arr[i + 1]:
            return False
    return True

	arr.sort()
	a, b = arr[0], arr[1]
	diff = b - a
	n = len(arr)
	for i in range(1, n):
		if arr[i] - arr[i - 1] != diff:
			return False
	return True


	arr_max, arr_min = -1_000_000, 1_000_000
    s = set()
    for i, num in enumerate(arr):
        s.add(num)
        arr_max = max(arr_max, num)
        arr_min = min(arr_min, num)
        
    n = len(arr)
    dif = (arr_max - arr_min) / (n - 1)
    # 所有数都一样大，差为0
    if dif == 0:
        return True
    # 差求出来不为整数，一定不是等差
    if dif != int(dif):
        return False
    # # 遍历第二次，验证每个元素是否在集合中
    # for i in range(1, n):
    # 	if arr_min + dif * i not in s:
    # 		return False
    # return True
    # 上面四行可以简写为：
    return all(arr_min + dif * i in s for i in range(1, n))
















































































