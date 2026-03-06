# 350. 两个数组的交集 II


def intersect(self, nums1: List[int], nums2: List[int]) -> List[int]:
    if len(nums1) > len(nums2):
        return self.intersect(nums2, nums1)
    
    m = collections.Counter()
    for num in nums1:
        m[num] += 1
    
    intersection = list()
    for num in nums2:
        if (count := m.get(num, 0)) > 0:
            intersection.append(num)
            m[num] -= 1
            if m[num] == 0:
                m.pop(num)
    
    return intersection




def intersect(self, nums1: List[int], nums2: List[int]) -> List[int]:
    nums1.sort()
    nums2.sort()

    length1, length2 = len(nums1), len(nums2)
    intersection = list()
    index1 = index2 = 0
    while index1 < length1 and index2 < length2:
        if nums1[index1] < nums2[index2]:
            index1 += 1
        elif nums1[index1] > nums2[index2]:
            index2 += 1
        else:
            intersection.append(nums1[index1])
            index1 += 1
            index2 += 1
    
    return intersection








