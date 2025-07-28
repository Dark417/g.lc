# 496. 下一个更大元素 I

def nextGreaterElement(self, nums1: List[int], nums2: List[int]) -> List[int]:
    res = {}
    stack = []
    for num in reversed(nums2):
        while stack and num >= stack[-1]:
            stack.pop()
        res[num] = stack[-1] if stack else -1
        stack.append(num)
    return [res[num] for num in nums1]





def nextGreaterElement(self, nums1: List[int], nums2: List[int]) -> List[int]:
    res = []
    stack = []
    m = {i:-1 for i in nums2}
    for i in nums2:
        while stack and i > stack[-1]:
            small = stack.pop()
            m[small] = i
        stack.append(i)
        
    return [m[i] for i in nums1]


def nextGreaterElement(self, nums1: List[int], nums2: List[int]) -> List[int]:
    stack = []
    res_dict = {i:-1 for i in nums2}
    for i in nums2:
        while stack and i > stack[-1]:
            small = stack.pop()
            res_dict[small] = i
        stack.append(i)
    res = []
    for j in nums1:
        res.append(res_dict[j])
    return re
s

def nextGreaterElement(self, nums1: List[int], nums2: List[int]) -> List[int]:
    m, n = len(nums1), len(nums2)
    res = [0] * m
    for i in range(m):
        j = nums2.index(nums1[i])
        k = j + 1
        while k < n and nums2[k] < nums2[j]:
            k += 1
        res[i] = nums2[k] if k < n else -1
    return res












