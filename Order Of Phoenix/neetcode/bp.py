


Blind75

#Array & Hashing

# ez
# Contains Duplicate
def hasDuplicate(self, nums: List[int]) -> bool:
    cnt = Counter(nums)
    for i in cnt:
        if cnt[i] > 1:
            return True
    return False

def hasDuplicate(self, nums: List[int]) -> bool:
    nums.sort()
    for i in range(len(nums) - 1):
        if nums[i] == nums[i + 1]:
            return True
    return False


# Valid Anagram  
def isAnagram(self, s: str, t: str) -> bool:
	return Counter(s) == Counter(t)

# Two Sum
def twoSum(self, nums: List[int], target: int) -> List[int]:
    dc = {}
    for i in range(len(nums)):
        n = nums[i]
        if target - nums[i] in dc:
            return [dc[target - nums[i]], i]
        dc[n] = i


# mid
# Group Anagrams
def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
    res = defaultdict(list)
    for s in strs:
        sortedS = ''.join(sorted(s))
        res[sortedS].append(s)
    return list(res.values())

def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
    res = defaultdict(list)
    for s in strs:
        count = [0] * 26
        for c in s:
            count[ord(c) - ord('a')] += 1
        res[tuple(count)].append(s)
    return list(res.values())


# Top K Frequent Elements   	
# Encode and Decode Strings   	
# Product of Array Except Self
def productExceptSelf(self, nums: List[int]) -> List[int]:
    n = len(nums)
    res = [0] * n
    pref = [0] * n
    suff = [0] * n

    pref[0] = suff[n - 1] = 1
    for i in range(1, n):
        pref[i] = nums[i - 1] * pref[i - 1]
    for i in range(n - 2, -1, -1):
        suff[i] = nums[i + 1] * suff[i + 1]
    for i in range(n):
        res[i] = pref[i] * suff[i] 
    return res

def productExceptSelf(self, nums: List[int]) -> List[int]:
    res = [1] * (len(nums))

    prefix = 1
    for i in range(len(nums)):
        res[i] = prefix
        prefix *= nums[i]
    postfix = 1
    for i in range(len(nums) - 1, -1, -1):
        res[i] *= postfix
        postfix *= nums[i]
    return res

# Longest Consecutive Sequence
#hash
def longestConsecutive(self, nums: List[int]) -> int:
    mp = defaultdict(int)
    res = 0

    for num in nums:
        if not mp[num]:
            mp[num] = mp[num - 1] + mp[num + 1] + 1
            mp[num - mp[num - 1]] = mp[num]
            mp[num + mp[num + 1]] = mp[num]
            res = max(res, mp[num])
    return res

#set while
def longestConsecutive(self, nums: List[int]) -> int:
    numSet = set(nums)
    longest = 0

    for num in numSet:
        if (num - 1) not in numSet:
            length = 1
            while (num + length) in numSet:
                length += 1
            longest = max(length, longest)
    return longest


#Two Pointers
# Valid Palindrome
def isPalindrome(self, s: str) -> bool:
    t = ""
    for c in s:
        if c.lower() in "abcdefghijklmnopqrstuvwxyz0123456789":
            t += c.lower()
    if len(t) == 1:
        return True
    i = 0
    j = len(t) - 1
    while i < j:
        if t[i].lower() != t[j].lower():
            return False
        i += 1
        j -= 1
    return True

def isPalindrome(self, s: str) -> bool:
    l, r = 0, len(s) - 1

    while l < r:
        while l < r and not self.alphaNum(s[l]):
            l += 1
        while r > l and not self.alphaNum(s[r]):
            r -= 1
        if s[l].lower() != s[r].lower():
            return False
        l, r = l + 1, r - 1
    return True

def alphaNum(self, c):
    return (ord('A') <= ord(c) <= ord('Z') or 
            ord('a') <= ord(c) <= ord('z') or 
            ord('0') <= ord(c) <= ord('9'))
        
# 3Sum

# Container With Most Water







        









































































































