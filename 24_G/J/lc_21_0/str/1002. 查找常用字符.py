# 1002. 查找常用字符



def commonChars(self, A: List[str]) -> List[str]:
    res = []
    checked = set()
    for s in A[0]:
        if s not in checked:
            c = map(lambda x: x.count(s), A)
            x = min(c)
            if x >= 1:
                res.extend([s]*x)
                checked.add(s)
    return res



def commonChars(self, A: List[str]) -> List[str]:
    minfreq = [float("inf")] * 26
    for word in A:
        freq = [0] * 26
        for ch in word:
            freq[ord(ch) - ord("a")] += 1
        for i in range(26):
            minfreq[i] = min(minfreq[i], freq[i])
    
    ans = list()
    for i in range(26):
        ans.extend([chr(i + ord("a"))] * minfreq[i])
    return ans










