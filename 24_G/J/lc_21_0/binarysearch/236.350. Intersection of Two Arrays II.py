"""
236.350. Intersection of Two Arrays II
两个数组的交集 II


Given two arrays, write a function to compute their intersection.

Example 1:

Input: nums1 = [1,2,2,1], nums2 = [2,2]
Output: [2,2]
Example 2:

Input: nums1 = [4,9,5], nums2 = [9,4,9,8,4]
Output: [4,9]
Note:

Each element in the result should appear as many times as it shows in both arrays.
The result can be in any order.
Follow up:

What if the given array is already sorted? How would you optimize your algorithm?
What if nums1's size is small compared to nums2's size? Which algorithm is better?
What if elements of nums2 are stored on disk, and the memory is limited such that you cannot load all elements into the memory at once?


"""

def intersect(self, nums1, nums2):
    inter = set(nums1) & set(nums2)
    l = []
    for i in inter:
        l += [i] * min(nums1.count(i), nums2.count(i))  
    return l



def intersect(self, nums1, nums2):
    a, b = map(collections.Counter, (nums1, nums2))
    return list((a & b).elements())

def intersect(self, nums1, nums2):
    C = collections.Counter
    return list((C(nums1) & C(nums2)).elements())
    
def intersect(self, nums1, nums2):
    return list((collections.Counter(nums1) & collections.Counter(nums2)).elements())



def intersect(self, nums1, nums2):
    c1, c2 = Counter(nums1), Counter(nums2)
    return sum([[num] * min(c1[num], c2[num]) for num in c1 & c2], [])

    return sum([[i]*min(nums1.count(i),nums2.count(i)) for i in set(nums1)&set(nums2)],[])


def intersect(self, nums1, nums2):
    from collections import Counter
    c1 = Counter(nums1)
    c2 = Counter(nums2)
    return list((c1&c2).elements())



def intersect(self, nums1, nums2):
    nums1, nums2 = sorted(nums1), sorted(nums2)
    pt1 = pt2 = 0
    res = []

    while True:
        try:
            if nums1[pt1] > nums2[pt2]:
                pt2 += 1
            elif nums1[pt1] < nums2[pt2]:
                pt1 += 1
            else:
                res.append(nums1[pt1])
                pt1 += 1
                pt2 += 1
        except IndexError:
            break

    return res


def intersect(self, nums1, nums2):
    counts = {}
    res = []

    for num in nums1:
        counts[num] = counts.get(num, 0) + 1

    for num in nums2:
        if num in counts and counts[num] > 0:
            res.append(num)
            counts[num] -= 1

    return res



def intersect(self, nums1, nums2):
    counts = collections.Counter(nums1)
    res = []
    for num in nums2:
        if counts[num] > 0:
            res += num,
            counts[num] -= 1

    return res




def intersect(self, nums1: List[int], nums2: List[int]) -> List[int]:
    s1 = {}
    res = []
    for e in nums1:
        if e not in s1:
            s1[e] = 0
        s1[e] += 1
    for e in nums2:
        if e in s1 and s1[e] > 0:
            res.append(e)
            s1[e] -= 1
    return res


def intersect(self, nums1: List[int], nums2: List[int]) -> List[int]:
    res = []
    for e in nums1:
        if e in nums2:
            res.append(e)
            nums2.remove(e)
    return res












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



def intersect(self, nums1: [int], nums2: [int]) -> [int]:
    nums1.sort()
    nums2.sort()
    r = []
    left, right = 0, 0
    while left < len(nums1) and right < len(nums2):
        if nums1[left] < nums2[right]:
            left += 1
        elif nums1[left] == nums2[right]:
            r.append(nums1[left])
            left += 1
            right += 1    
        else:
            right += 1
    return r






































































