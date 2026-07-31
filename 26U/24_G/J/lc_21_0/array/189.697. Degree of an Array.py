"""
189.697. Degree of an Array
数组的度

Given a non-empty array of non-negative integers nums, the degree of this array is defined as the maximum frequency of any one of its elements.

Your task is to find the smallest possible length of a (contiguous) subarray of nums, that has the same degree as nums.

Example 1:
Input: [1, 2, 2, 3, 1]
Output: 2
Explanation: 
The input array has a degree of 2 because both elements 1 and 2 appear twice.
Of the subarrays that have the same degree:
[1, 2, 2, 3, 1], [1, 2, 2, 3], [2, 2, 3, 1], [1, 2, 2], [2, 2, 3], [2, 2]
The shortest length is 2. So return 2.
Example 2:
Input: [1,2,2,3,1,4,2]
Output: 6
Note:

nums.length will be between 1 and 50,000.
nums[i] will be an integer between 0 and 49,999.

"""



[i for i, v in enumerate(l) if v == 1]



def findShortestSubArray(self, nums):
    left, right, count = {}, {}, {}
    for i, x in enumerate(nums):
        if x not in left: left[x] = i
        right[x] = i
        count[x] = count.get(x, 0) + 1

    ans = len(nums)
    degree = max(count.values())
    for x in count:
        if count[x] == degree:
            ans = min(ans, right[x] - left[x] + 1)

    return ans


# lee
def findShortestSubArray(self, A):
    first, count, res, degree = {}, {}, 0, 0
    for i, a in enumerate(A):
        first.setdefault(a, i)
        count[a] = count.get(a, 0) + 1
        if count[a] > degree:
            degree = count[a]
            res = i - first[a] + 1
        elif count[a] == degree:
            res = min(res, i - first[a] + 1)
    return res


def findShortestSubArray(self, nums):
    first, last = {}, {}
    for i, v in enumerate(nums):
        first.setdefault(v, i)
        last[v] = i
    c = collections.Counter(nums)
    degree = max(c.values())
    return min(last[v] - first[v] + 1 for v in c if c[v] == degree)



def findShortestSubArray(self, nums: List[int]) -> int:
    C = {}
    for i, n in enumerate(nums):
        if n in C: C[n].append(i)
        else: C[n] = [i]
    M = max([len(i) for i in C.values()])
    return min([i[-1]-i[0] for i in C.values() if len(i) == M]) + 1




def findShortestSubArray(self, nums):
    cnt, seen = collections.Counter(nums), collections.defaultdict(list)
    degree = max(cnt.values())
    for i, v in enumerate(nums): seen[v].append(i)
    return min(seen[v][-1] - seen[v][0] + 1 for v in cnt if cnt[v] == degree)



def findShortestSubArray(self, nums):
    nums_map, deg, min_len = collections.defaultdict(list), 0, float('inf')
    for index, num in enumerate(nums):
        nums_map[num].append(index)
        deg = max(deg, len(nums_map[num]))
    for num, indices in nums_map.items():
        if len(indices) == deg:
            min_len = min(min_len, indices[-1] - indices[0] + 1)
    return min_len


def findShortestSubArray(self, nums):
    nums_map, deg, min_len = collections.defaultdict(list), 0, float('inf')
    for index, num in enumerate(nums):
        nums_map[num].append(index)
        if len(nums_map[num]) == deg:
            min_len = min(min_len, nums_map[num][-1] - nums_map[num][0] + 1)
        elif len(nums_map[num]) > deg:
            deg = len(nums_map[num])
            min_len = nums_map[num][-1] - nums_map[num][0] + 1
    return min_len





def findShortestSubArray(self, nums: List[int]) -> int:
    dict_ = {}
    dp = [0] * (max(nums)+1)
    for i,j in enumerate(nums):   # i代表索引，j代表索引的值
        dict_[j] = i     #j值最新出现的索引
        dp[j] += 1       #求出j一共出现了几次,这里的索引代表j值
    max_=max(dp)
    min_=float("inf")
    for i in range(len(dp)):
        if dp[i] == max_:     #求出出现频次最高的索引值，在这里i与j是相等的
            b=dict_[i]        #找出最后一次出现b的索引
            c=nums.index(i)   #找出第一次出现b的索引
            d=b-c+1           #求出最短的连续子数组
            min_ = min(min_,d)
    return min_














































































