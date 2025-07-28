"""
042.3. Longest Substring Without Repeating Characters
无重复字符的最长子串

Given a string, find the length of the longest substring without repeating characters.

Example 1:

Input: "abcabcbb"
Output: 3 
Explanation: The answer is "abc", with the length of 3. 
Example 2:

Input: "bbbbb"
Output: 1
Explanation: The answer is "b", with the length of 1.
Example 3:

Input: "pwwkew"
Output: 3
Explanation: The answer is "wke", with the length of 3. 
             Note that the answer must be a substring, "pwke" is a subsequence and not a substring.

"""

def lengthOfLongestSubstring(self, s):
    dic, res, start, = {}, 0, 0
    for i, ch in enumerate(s):
        if ch in dic:
            res = max(res, i-start)
            start = max(start, dic[ch]+1)
        dic[ch] = i
    return max(res, len(s)-start)

    
def lengthOfLongestSubstring(self, s: str) -> int:
    n = len(s)
    res = 0
    l = r = 0
    window = {}
    while r < n:
        if s[r] not in window:
            window[s[r]] = r
        else:
            if window[s[r]] >= l:
                l = window[s[r]] + 1
            window[s[r]] = r
        res = max(res, r - l + 1)
        r += 1
    return res



def lengthOfLongestSubstring(self, s: str) -> int:
    n = len(s)
    res = l = r = 0
    window = {}
    for r in range(n):
        if s[r] in window  and window[s[r]] >= l:
            l = window[s[r]] + 1
        window[s[r]] = r
        res = max(res, r - l + 1)
    return res


def lengthOfLongestSubstring(self, s: str) -> int:
    n = len(s)
    res = 0
    l = r = 0
    window = {}
    while r < n:
        if s[r] in window  and window[s[r]] >= l:
            l = window[s[r]] + 1
        window[s[r]] = r
        res = max(res, r - l + 1)
        r += 1
    return res








def lengthOfLongestSubstring(self, s):
    seen = ''
    mx = 0
    for c in s:
        if c not in seen:
            seen+=c
        else:
            seen = seen[seen.index(c) + 1:] + c
        mx = max(mx, len(seen))
    return mx

    
def lengthOfLongestSubstring(self, s: str) -> int:
    occ = set()
    n = len(s)
    rk, ans = -1, 0
    for i in range(n):
        if i != 0:
            occ.remove(s[i - 1])
        while rk + 1 < n and s[rk + 1] not in occ:
            occ.add(s[rk + 1])
            rk += 1
        ans = max(ans, rk - i + 1)
    return ans



def lengthOfLongestSubstring(self, s: str) -> int:
    if not s:return 0
    left = 0
    lookup = set()
    n = len(s)
    max_len = 0
    cur_len = 0
    for i in range(n):
        cur_len += 1
        while s[i] in lookup:
            lookup.remove(s[left])
            left += 1
            cur_len -= 1
        if cur_len > max_len:max_len = cur_len
        lookup.add(s[i])
    return max_len




def lengthOfLongestSubstring(self, string):
    longest = 0
    left, right = 0, 0
    chars = set()
    while left < len(string) and right < len(string):
        if string[right] not in chars:
            chars.add(string[right])
            right += 1
            longest = max(longest, right - left)
        else:
            chars.remove(string[left])
            left += 1
    return longest






def lengthOfLongestSubstring(self, s: str) -> int:
    seen = {}
    l = 0
    output = 0
    for r in range(len(s)):
        if s[r] not in seen:
            output = max(output,r-l+1)
        else:
            if seen[s[r]] < l:
                output = max(output,r-l+1)
            else:
                l = seen[s[r]] + 1
        seen[s[r]] = r
    return output






























