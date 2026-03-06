# 325. 和等于 k 的最长子数组长度


def maxSubArrayLen(self, nums: List[int], k: int) -> int:
    pre_dic = {0: 0}
    res, pre_sum = 0, 0
    for i in range(len(nums)):
        pre_sum += nums[i]
        if pre_sum - k in pre_dic:
            res = max(res, i + 1 - pre_dic[pre_sum - k])
        if pre_sum not in pre_dic:
            pre_dic[pre_sum] = i + 1
    return res




def maxSubArrayLen(self, nums: List[int], k: int) -> int:
    dic = {0:-1}
    cur_prefix = 0
    res_len = 0
    for idx, val in enumerate(nums):
        cur_prefix += val
        if (cur_prefix-k) in dic:
            res_len = max(res_len, idx-dic[cur_prefix-k])
        if cur_prefix not in dic:
            dic[cur_prefix] = idx

    return res_len



def maxSubArrayLen(self, nums: List[int], k: int) -> int:
    hashmap = {}
    pre_sum = []
    temp = 0
    for i in range(len(nums)):
        temp += nums[i]
        pre_sum.append(temp)
        if temp not in hashmap.keys():
            hashmap[temp] = i
    ans = 0
    for i in range(len(nums)):
        if pre_sum[i] == k:
            ans = max(ans,i + 1)
        elif pre_sum[i] - k in hashmap.keys():
            ans = max(ans,i - hashmap[pre_sum[i] - k])       
    return ans




def maxSubArrayLen(self, nums: List[int], k: int) -> int:
    n = len(nums)
    presum = [0 for _ in range(n+1)]
    for i, num in enumerate(nums):
        presum[i+1] = presum[i]+num
        
    res = 0
    m = defaultdict(int) # {presum: index}
    for j in range(n+1):
        # find complementary
        if presum[j]-k in m:
            res = max(res, j-m[presum[j]-k])
        
        # get the earliest occurance
        if presum[j] not in m:
            m[presum[j]] = j

    return res





