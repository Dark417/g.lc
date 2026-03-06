"""
155.136. Single Number
只出现一次的数字



Given a non-empty array of integers, every element appears twice except for one. Find that single one.

Note:

Your algorithm should have a linear runtime complexity. Could you implement it without using extra memory?

Example 1:

Input: [2,2,1]
Output: 1
Example 2:

Input: [4,1,2,1,2]
Output: 4

"""


# caiheke
def singleNumber1(self, nums):
    dic = {}
    for num in nums:
        dic[num] = dic.get(num, 0)+1
    for key, val in dic.items():
        if val == 1:
            return key

    
def singleNumber3(self, nums):
    return 2*sum(set(nums))-sum(nums)
    
def singleNumber4(self, nums):
    return reduce(lambda x, y: x ^ y, nums)
    
def singleNumber(self, nums):
    return reduce(operator.xor, nums)




def singleNumber(self, nums: List[int]) -> int:
    return reduce(lambda x, y: x^y, nums, 0)


def singleNumber2(self, nums):
    res = 0
    for num in nums:
        res ^= num
    return res


return 2 * sum(set(nums)) - sum(nums)





def singleNumber(self, nums: List[int]) -> int:
    for i, v in Counter(nums).items():
        if v == 1:
            return i


def singleNumber(self, nums: List[int]) -> int:
    hash_table = defaultdict(int)
    for i in nums:
        hash_table[i] += 1
    
    for i in hash_table:
        if hash_table[i] == 1:
            return i



def singleNumber(self, nums):
    no_duplicate_list = []
    for i in nums:
        if i not in no_duplicate_list:
            no_duplicate_list.append(i)
        else:
            no_duplicate_list.remove(i)
    return no_duplicate_list.pop()



























































