"""
238.1213. Intersection of Three Sorted Arrays
三个有序数组的交集

给出三个均为 严格递增排列 的整数数组 arr1，arr2 和 arr3。

返回一个由 仅 在这三个数组中 同时出现 的整数所构成的有序数组。

 

示例：

输入: arr1 = [1,2,3,4,5], arr2 = [1,2,5,7,9], arr3 = [1,3,4,5,8]
输出: [1,5]
解释: 只有 1 和 5 同时在这三个数组中出现.
 

提示：

1 <= arr1.length, arr2.length, arr3.length <= 1000
1 <= arr1[i], arr2[i], arr3[i] <= 2000

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/intersection-of-three-sorted-arrays
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。


"""


def arraysIntersection(self, arr1: List[int], arr2: List[int], arr3: List[int]) -> List[int]:
    return [k for k, v in Counter(arr1+arr2+arr3).items() if v == 3]

def arraysIntersection(self, arr1: List[int], arr2: List[int], arr3: List[int]) -> List[int]:
    s = Counter(arr1+arr2+arr3)
    return [k for k in s if s[k] == 3]

	return sorted(list(set(arr1)&set(arr2)&set(arr3)))


def arraysIntersection(self, arr1: List[int], arr2: List[int], arr3: List[int]) -> List[int]:
    i1,i2,i3 =0,0,0
    L = len(arr1)
    result = []
    while i1<L and i2<L and i3<L:
        if arr1[i1]== arr2[i2] and arr1[i1]==arr3[i3]:
            result.append(arr1[i1])
            i1+=1
            i2+=1
            i3+=1
        else:
            if arr1[i1] <= arr2[i2] and arr1[i1] <= arr3[i3]:
                i1 += 1
            elif arr2[i2] <= arr1[i1] and arr2[i2] <= arr3[i3]:
                i2 += 1
            elif arr3[i3] <= arr1[i1] and arr3[i3] <= arr2[i2]:
                i3 += 1
    return result































































































