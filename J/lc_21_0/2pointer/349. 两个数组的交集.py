# 349. 两个数组的交集

# 遍历较小的集合并判断元素是否在另一个集合中需要 O(\min(m,n))O(min(m,n)) 的时间


def intersection(self, nums1: List[int], nums2: List[int]) -> List[int]:
    set1 = set(nums1)
    set2 = set(nums2)
    return self.set_intersection(set1, set2)

def set_intersection(self, set1, set2):
    if len(set1) > len(set2):
        return self.set_intersection(set2, set1)
    return [x for x in set1 if x in set2]




def intersection(self, nums1: List[int], nums2: List[int]) -> List[int]:
    nums1.sort()
    nums2.sort()
    length1, length2 = len(nums1), len(nums2)
    intersection = list()
    index1 = index2 = 0
    while index1 < length1 and index2 < length2:
        num1 = nums1[index1]
        num2 = nums2[index2]
        if num1 == num2:
            # 保证加入元素的唯一性
            if not intersection or num1 != intersection[-1]:
                intersection.append(num1)
            index1 += 1
            index2 += 1
        elif num1 < num2:
            index1 += 1
        else:
            index2 += 1



















