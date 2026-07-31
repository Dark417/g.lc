"""
235.349. Intersection of Two Arrays
两个数组的交集

Given two arrays, write a function to compute their intersection.

Example 1:

Input: nums1 = [1,2,2,1], nums2 = [2,2]
Output: [2]
Example 2:

Input: nums1 = [4,9,5], nums2 = [9,4,9,8,4]
Output: [9,4]
Note:

Each element in the result must be unique.
The result can be in any order.





"""

intersection = lambda *p: list(set(p[1]) & set(p[2]))

ans = lambda *p: list(set(p[0]) & set(p[1]))
return ans(nums1,nums2)





def set_intersection(self, set1, set2):
        return [x for x in set1 if x in set2]
        
def intersection(self, nums1, nums2): 
    set1 = set(nums1)
    set2 = set(nums2)
    
    if len(set1) < len(set2):
        return self.set_intersection(set1, set2)
    else:
        return self.set_intersection(set2, set1)



def intersection(self, nums1, nums2):
    set1 = set(nums1)
    set2 = set(nums2)
    return list(set2 & set1)


def intersection(self, nums1, nums2):
    return list(set(nums1) & set(nums2))



def intersection(self, nums1, nums2):
    res = []
    for i in nums1:
        if i not in res and i in nums2:
            res.append(i)
    
    return res



def intersection(self, nums1, nums2):
    res = []
    map = {}
    for i in nums1:
        map[i] = map[i]+1 if i in map else 1
    for j in nums2:
        if j in map and map[j] > 0:
            res.append(j)
            map[j] = 0
    
    return res


def intersection(self, nums1, nums2):
    res = []
    nums1.sort()
    nums2.sort()
    i = j = 0
    while (i < len(nums1) and j < len(nums2)):
        if nums1[i] > nums2[j]:
            j += 1
        elif nums1[i] < nums2[j]:
            i += 1
        else:
            if not (len(res) and nums1[i] == res[len(res)-1]):
                res.append(nums1[i])
            i += 1
            j += 1
    
    return res


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
    return intersection








# binary search
"""
public int[] intersection(int[] nums1, int[] nums2) {
  Set<Integer> set = new HashSet<>();
  Arrays.sort(nums2);
  for (int target : nums1) {
    if (binarySearch(nums2, target) && !set.contains(target)) {
      set.add(target);
    }
  }
  int index = 0;
  int[] res = new int[set.size()];
  for (int num : set) {
    res[index++] = num;
  }
  return res;
}
public boolean binarySearch(int[] nums, int target) {
  int left = 0, right = nums.length - 1;
  while (left <= right) {
    int mid = left + (right - left) / 2;
    if (nums[mid] == target) {
      return true;
    } else if (nums[mid] > target) {
      right = mid - 1;
    } else if (nums[mid] < target) {
      left = mid + 1;
    }
  }
  return false;
}


"""






















































