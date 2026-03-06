# 1768. 交替合并字符串

def mergeAlternately(self, w1, w2):
    return ''.join(a + b for a, b in zip_longest(w1, w2, fillvalue=''))

def mergeAlternately(self, word1: str, word2: str) -> str:
    return "".join(sum(zip_longest(word1, word2, fillvalue=""), ()))





def mergeAlternately(self, word1: str, word2: str) -> str:
    if not word2:
        return word1
    if not word1:
        return word2
    l = min(len(word1), len(word2))
    s = ""
    for i in range(l):
        s += word1[i] + word2[i]
    if len(word1) == l:
        s += word2[l:]
    if len(word2) == l:
        s += word1[l:]
    return s





















