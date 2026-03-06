"""
169.1. Two Sum
两数之和

Given an array of integers, return indices of the two numbers such that they add up to a specific target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

Example:

Given nums = [2, 7, 11, 15], target = 9,

Because nums[0] + nums[1] = 2 + 7 = 9,
return [0, 1].


"""



# dictionary 
def twoSum1(self, nums, target):
    dic = {}
    for i, num in enumerate(nums):
        if target-num in dic:
            return (dic[target-num]+1, i+1)
        dic[num] = i
 

# two-pointer       
def twoSum(self, nums, target):
    nums = enumerate(nums)
    nums = sorted(nums, key=lambda x:x[1])
    l, r = 0, len(nums)-1
    while l < r:
        if nums[l][1]+nums[r][1] == target:
            return sorted([nums[l][0]+1, nums[r][0]+1])
        elif nums[l][1]+nums[r][1] < target:
            l += 1
        else:
            r -= 1


def twoSum(self, nums: List[int], target: int) -> List[int]:
    for i in range(len(nums)-1):
        for j in range(i+1,len(nums)):
            if nums[i] + nums[j] == target:
                return [i,j]







def twoSum(nums, target):
    lens = len(nums)
    j=-1
    for i in range(lens):
        if (target - nums[i]) in nums:
            if (nums.count(target - nums[i]) == 1)&(target - nums[i] == nums[i]):#如果num2=num1,且nums中只出现了一次，说明找到是num1本身。
                continue
            else:
                j = nums.index(target - nums[i],i+1) #index(x,i+1)是从num1后的序列后找num2                
                break
    if j>0:
        return [i,j]
    else:
        return []



def twoSum(nums, target):
    lens = len(nums)
    j=-1
    for i in range(1,lens):
        temp = nums[:i]
        if (target - nums[i]) in temp:
            j = temp.index(target - nums[i])
            break
    if j>=0:
        return [j,i]





"""
public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> map = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        map.put(nums[i], i);
    }
    for (int i = 0; i < nums.length; i++) {
        int complement = target - nums[i];
        if (map.containsKey(complement) && map.get(complement) != i) {
            return new int[] { i, map.get(complement) };
        }
    }
    throw new IllegalArgumentException("No two sum solution");
}
"""



def twoSum(nums, target):
    hashmap={}
    for ind,num in enumerate(nums):
        hashmap[num] = ind
    for i,num in enumerate(nums):
        j = hashmap.get(target - num)
        if j is not None and i!=j:
            return [i,j]


def twoSum(self, nums, target):
    dic = {}
    for i, n in enumerate(nums): 
        if n in dic:
            return [dic[n], i]
        dic[target-n] = i




def twoSum(self, num, target):
    map = {}
    for i in range(len(num)):
        if num[i] not in map:
            map[target - num[i]] = i + 1
        else:
            return map[num[i]], i + 1
    return -1, -1




def twoSum(self, nums, target):
    d={}
    for i,num in enumerate(nums):
        if target-num in d:
            return d[target-num], i
        d[num]=i




def twoSum(self, nums, target):
    d = dict()
    for index,num in enumerate(nums):
        if d.get(num) == None:
            d[target - num] = index
        else:
            return [d.get(num), index]



def twoSum(self, nums, target):
    d={}
    for i, n in enumerate(nums):
        if d.has_key(n):
            return (d[n]+1, i+1)
        else:
            d[target-n]=i
    return (0,0)



def twoSum(self, nums, target):
    index = {}
    for i, x in enumerate(nums):
        if target - x in index:
            return [index[target - x], i]
        index[x] = i







"""
public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> map = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int complement = target - nums[i];
        if (map.containsKey(complement)) {
            return new int[] { map.get(complement), i };
        }
        map.put(nums[i], i);
    }
    throw new IllegalArgumentException("No two sum solution");
}
"""














































































