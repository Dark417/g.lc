# 159. 至多包含两个不同字符的最长子串

def lengthOfLongestSubstringTwoDistinct(self, s: 'str') -> 'int':
	k = 2
	n = len(s) 
    if k == 0 or n == 0:
        return 0
    left, right = 0, 0
    hashmap = defaultdict()
    max_len = 1
    while right < n:
        hashmap[s[right]] = right
        right += 1
		if len(hashmap) == k + 1:
            del_idx = min(hashmap.values())
            del hashmap[s[del_idx]]
            left = del_idx + 1
        max_len = max(max_len, right - left)
    return max_len





def lengthOfLongestSubstringTwoDistinct(self, s: 'str') -> 'int':
    n = len(s) 
    if n < 3:
        return n
    left, right = 0, 0
    hashmap = defaultdict()
    max_len = 2
    while right < n:
        if len(hashmap) < 3:
            hashmap[s[right]] = right
            right += 1
			if len(hashmap) == 3:
	            del_idx = min(hashmap.values())
	            del hashmap[s[del_idx]]
            	left = del_idx + 1
        max_len = max(max_len, right - left)
    return max_len


    
def lengthOfLongestSubstringTwoDistinct(self, s: 'str') -> 'int':
	K = 2
	if len(s) < K:
		return len(s)
	res = 0
	n = len(s)
	window = {}
	l = r = 0
	while r < n:
		window[s[r]] = window.get(s[r], 0) +1
		while len(window) > K:
			window[s[l]] -= 1
			if window[s[l]] == 0:
				del window[s[l]]
			l += 1
		res = max(res, r - l + 1)
		r += 1
	return res
























