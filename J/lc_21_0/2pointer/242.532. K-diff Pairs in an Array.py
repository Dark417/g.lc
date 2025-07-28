"""
242.532. K-diff Pairs in an Array
数组中的K-diff数对

Given an array of integers and an integer k, you need to find the number of unique k-diff pairs in the array. Here a k-diff pair is defined as an integer pair (i, j), where i and j are both numbers in the array and their absolute difference is k.

Example 1:
Input: [3, 1, 4, 1, 5], k = 2
Output: 2
Explanation: There are two 2-diff pairs in the array, (1, 3) and (3, 5).
Although we have two 1s in the input, we should only return the number of unique pairs.
Example 2:
Input:[1, 2, 3, 4, 5], k = 1
Output: 4
Explanation: There are four 1-diff pairs in the array, (1, 2), (2, 3), (3, 4) and (4, 5).
Example 3:
Input: [1, 3, 1, 5, 4], k = 0
Output: 1
Explanation: There is one 0-diff pair in the array, (1, 1).
Note:
The pairs (i, j) and (j, i) count as the same pair.
The length of the array won't exceed 10,000.
All the integers in the given input belong to the range: [-1e7, 1e7].

"""


# lee
def findPairs(self, nums, k):
    res = 0
    c = collections.Counter(nums)
    for i in c:
        if k > 0 and i + k in c or k == 0 and c[i] > 1:
            res += 1
    return res


def findPairs(self, nums, k):
    c = collections.Counter(nums)
    return  sum(k > 0 and i + k in c or k == 0 and c[i] > 1 for i in c)








def findPairs(self, nums, k):
	nums.sort()
    res , dic= 0 , {}
    for i in nums:
        dic[i] = dic[i]+1 if i in dic else 1
    for i in dic.keys():
        if (i+k in dic and k>0) or (k==0 and dic[i]>1):
            res += 1
    return res 




def findPairs(self, nums: List[int], k: int) -> int:
    if k < 0:
        return 0
    if k == 0:
        return len(set([i for i in nums if nums.count(i)>=2]))
    cl = [i+k for i in nums]
    return len(set(cl)&set(nums))



def findPairs(self, nums: List[int], k: int) -> int:
    if k < 0:
        return 0
    if k == 0:
        c = Counter(nums)
        return len([i for i in c if c[i] > 1])
    s = set(nums)
    return len([i for i in s if i + k in s])


def findPairs(self, nums: List[int], k: int) -> int:
    if k < 0:
        return 0
    if k == 0:
        return len(set([i for i in nums if nums.count(i) >= 2]))
    return len(set(i + k for i in nums) & set(nums))










def findPairs(self, nums: List[int], k: int) -> int:
    numDict = {}
    for i in nums:
        numDict[i] = numDict.get(i, 0) + 1
    res = 0
    for key in numDict.keys():
        if k == 0:
            if numDict[key] > 1:
                res += 1
        elif k > 0:
            if numDict.get(k+key) is not None:
                res += 1
        else:
            break
    return res



def findPairs(self, nums, k):
    count = 0
    nums.sort()
    
    slow = 0
    fast = 1
    size = len(nums)
    
    while fast < size:
        if nums[fast] - nums[slow] < k: # case 1, diff is less than k
            fast += 1
        elif nums[fast] - nums[slow] > k: # case 2, diff is greater than k
            slow += 1
        else: # case 3, diff is equal to k so increment the count!
            count += 1
            fast += 1
            slow += 1
            
            #Now ignore any duplicates, both slow and fast could be pointing to duplicates
            while slow < size-1 and nums[slow] == nums[slow-1]:
                slow += 1
                
            while fast < size-1 and nums[fast] == nums[fast-1]:
                fast += 1
                
        if fast <= slow: # fast should be atleast one more than slow
            fast = slow + (slow - fast) + 1
    return count





def findPairs(self, nums, k):
    if k < 0: return 0
    numsSet, pairsSet = set(), set()
    for num1 in nums:
        for num2 in [num1 + k, num1 - k]:
            if num2 in numsSet:
                pairsSet.add(tuple(sorted([num1, num2])))
        numsSet.add(num1)
    return len(pairsSet)



def findPairs(self, nums: List[int], k: int) -> int:
	#If k is less than 0, then the result is 0 since we are looking fpr pairs with an ABSOLUTE difference of k.
    if k < 0:
        return 0
    
    count = Counter(nums)
    pairs = set([])
    
    for num in count.keys():
		#Special case: If k == 0, then there needs to be at least two occurences of a particular num in nums 
		#in order for there to be a pair (num, num).
        if k == 0:
            if count[num] > 1:
                pairs.add((num, num))
				
		#Regular case: k != 0. Simply check if num + k is a member of the array nums.
		#Insert the pair into the set of pairs (smallerNum, largerNum) so that there are no duplicate pairs.
        else:
            otherNum = num + k
            if otherNum in count:
                pairs.add((num, otherNum) if num <= otherNum else (otherNum, num))
                
    return len(pairs)



































































































































