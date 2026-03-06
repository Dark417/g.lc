# 560. 和为 K 的子数组
Counter没有key，忽略
Dict必须check

def subarraySum(self, nums, k):
    dic = Counter({0: 1})
    ret = pre_su m= 0
    for i in nums:
        pre_sum += i
        ret += dic[pre_sum - k]
        dic[pre_sum] += 1
    return ret


def subarraySum(self, nums, k):
    hashMap, presum, count = dict(), 0, 0 
    hashMap[0] = 1
    for num in nums:
        presum += num # record the current presum
        if presum - k in hashMap: 
            count += hashMap[presum-k]
        hashMap[presum] = hashMap.get(presum,0) + 1
    return count




def subarraySum(self, nums: List[int], k: int) -> int:
    c = pre = prex = i = j = 0
    n = len(nums)
    for i in range(n):
        pre += nums[i]
        if pre == k:
            c += 1
        elif pre < k:
            continue
        else:
            while pre > k and i > j:
                prex += nums[j]
                if pre - prex == k:
                    c += 1
                    j += 1
                    break
                j += 1
    
    return c

