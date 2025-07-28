# 424. 替换后的最长重复字符


def characterReplacement(self, s: str, k: int) -> int:
    num = [0] * 26
    n = len(s)
    mx = l = r = 0

    while r < n:
        num[ord(s[r]) - ord("A")] += 1
        mx = max(mx, num[ord(s[r]) - ord("A")])
        if r - l + 1 - mx > k:
            num[ord(s[l]) - ord("A")] -= 1
            l += 1
        r += 1
    
    return right - left


def characterReplacement(self, s, k):
    N = len(s)
    left, right = 0, 0 # [left, right] 都包含
    counter = collections.Counter()
    res = 0
    while right < N:
        counter[s[right]] += 1
        while right - left + 1 - counter.most_common(1)[0][1] > k:
            counter[s[left]] -= 1
            left += 1
        res = max(res, right - left + 1)
        right += 1
    return res


















