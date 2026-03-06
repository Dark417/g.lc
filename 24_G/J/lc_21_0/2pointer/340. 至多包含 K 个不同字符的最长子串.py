# 340. 至多包含 K 个不同字符的最长子串

def lengthOfLongestSubstringKDistinct(self, s: 'str', k: 'int') -> 'int':
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



def lengthOfLongestSubstringKDistinct(self, s: 'str', k: 'int') -> 'int':
    n = len(s) 
    if k == 0 or n == 0:
        return 0
    left, right = 0, 0
    hashmap = OrderedDict()
    max_len = 1
    while right < n:
        character = s[right]
        if character in hashmap:
            del hashmap[character]
        hashmap[character] = right
        right += 1
        if len(hashmap) == k + 1:
            _, del_idx = hashmap.popitem(last = False)
            left = del_idx + 1
        max_len = max(max_len, right - left)
    return max_len




















