"""
209.392. Is Subsequence
判断子序列


Given a string s and a string t, check if s is subsequence of t.

A subsequence of a string is a new string which is formed from the original string by 
deleting some (can be none) of the characters without disturbing the relative positions 
of the remaining characters. (ie, "ace" is a subsequence of "abcde" while "aec" is not).

Follow up:
If there are lots of incoming S, say S1, S2, ... , Sk where k >= 1B, and you want to 
check one by one to see if T has its subsequence. In this scenario, how would you change 
your code?

Credits:
Special thanks to @pbrother for adding this problem and creating all test cases.

 

Example 1:

Input: s = "abc", t = "ahbgdc"
Output: true
Example 2:

Input: s = "axc", t = "ahbgdc"
Output: false
 

Constraints:

0 <= s.length <= 100
0 <= t.length <= 10^4
Both strings consists only of lowercase characters.


https://leetcode.com/problems/is-subsequence/discuss/678389/Python-3-Solutions%3A-DP-2-pointers-and-follow-up-BS-explained
"""


def isSubsequence(self, s: str, t: str) -> bool:
    if len(s) == 0: return True
    i = 0
    for k in t:
        if k == s[i]:
            i += 1
            if i == len(s):
                return True
    return False



# if X and Y, X first!
def isSubsequence(self, s: str, t: str) -> bool:
    i = 0
    for c in t: 
        if i < len(s) and s[i] == c: i += 1
    return i == len(s)



def isSubsequence(self, s: str, t: str) -> bool:
    # 每个字符串都在长字符串中，且位置序号单调递增。
    c,curr_p=1,0
    for i in s:
        if i not in t:
            return False
        curr_p=t.index(i)
        t=t[curr_p+1:]
        c+=1
    return True



def isSubsequence(self, s, t):
    t = iter(t)
    return all(i in t for i in s) 



# chopper
def isSubsequence(self, s: str, t: str) -> bool: 
    loc = -1
    for a in s:
        loc = t.find(a, loc + 1)
        if loc == -1:
            return False
    return True


    start = 0
    for c in s:
        i = t.find(c, start)
        if i == -1:
            return False
        start = i + 1
    return True

def isSubsequence(self, s: str, t: str) -> bool:
	for i in range (0, len(s)):    
		try:
			index = t.index(s[i])
		except ValueError: 
			return False

		t = t[index+1:]

	return True



def isSubsequence(self, s: str, t: str) -> bool:
    k = 0
    for c in s:
        k = t.find(c, k) + 1
        if k == 0: return False
    return True 


def isSubsequence(self, s: str, t: str) -> bool:
    k = 0
    for c in s:
        try: k = t.index(c, k) + 1
        except: return False
    return True 


import re
def isSubsequence(self, s: str, t: str) -> bool:
    for c in s:
        try: k = re.search(c, t).start()
        except: return False
        t = t[k+1:]
    return True 




def isSubsequence(self, s, t):
    remainder_of_t = iter(t)
    for letter in s:
        if letter not in remainder_of_t:
            return False
    return True


def isSubsequence(self, s: str, t: str) -> bool:
    i = 0
    j = 0
    while i < len(s) and j < len(t):
        if s[i] == t[j]:
            i += 1
            j += 1
        else:
            j += 1    
    return i == len(s)


	if len(s) == 0:
        return True
    if len(t) == 0:
        return False 
    i, j = 0, 0
    while i < len(s) and j < len(t):
        if s[i] == t[j]:
            i += 1
        j += 1
    return True if i == len(s) else False


# two pointer
def isSubsequence(self, s, t):
    s_i, t_i = 0, 0
    while s_i < len(s) and t_i < len(t):
        s_i, t_i = s_i + (s[s_i] == t[t_i]), t_i + 1
    return s_i == len(s)



# dp
 def isSubsequence(self, s, t):
    s, t = "!" + s, "!" + t
    m, n = len(s), len(t)
    dp = [[0] * m for _ in range(n)] 
    for i in range(n): dp[i][0] = 1

    for i,j in product(range(1, n), range(1, m)):
        if s[j] == t[i]:
            dp[i][j] = dp[i-1][j-1]
        else:
            dp[i][j] = dp[i-1][j]
                
    return dp[-1][-1]




def isSubsequence(self, s, t):
    places = defaultdict(list)
    for i, symbol in enumerate(t):
        places[symbol].append(i)
    
    current_place = 0
    for symbol in s:
        current_ind = bisect.bisect_left(places[symbol], current_place)
        if current_ind >= len(places[symbol]):
            return False
        current_place = places[symbol][current_ind] + 1
        
    return True







def isSubsequence(self, s: str, t: str) -> bool:  
    from collections import defaultdict
    import bisect
    lookup = defaultdict(list)
    for idx, val in enumerate(t):
        lookup[val].append(idx)
    # print(lookup)
    loc = -1
    for a in s:
        j = bisect.bisect_left(lookup[a], loc + 1)
        if j >= len(lookup[a]): return False
        loc = lookup[a][j]
    return True





# binary search
# O(T + SlogT)
def isSubsequence(self, s, t):
    d = collections.defaultdict(list)
    for i in xrange(0, len(t)):
        d[t[i]].append(i)
    start = 0
    for c in s:
        idx = bisect.bisect_left(d[c], start)
        if len(d[c]) == 0 or idx >= len(d[c]):
            return False
        start = d[c][idx] + 1
    return True



def isSubsequence(self, s, t):     
    d = collections.defaultdict(list)
    for i,c in enumerate(t):
        d[c].append(i)
    start = 0 
    for c in s:
        if len(d[c]) == 0:                  # character in S do not contain in T
            return False
        curr = bisect.bisect_left(d[c], start)
        if curr == len(d[c]):              # the curr position returned in bisect do not contain in T 
            return False
        start = d[c][curr] + 1
    return True


















































