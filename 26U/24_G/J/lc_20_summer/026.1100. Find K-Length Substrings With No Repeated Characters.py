"""
026.1100. Find K-Length Substrings With No Repeated Characters
长度为 K 的无重复字符子串






"""
def numKLenSubstrNoRepeats(self, S: str, K: int) -> int:
                    
    return sum(1 for i in range(len(S)-K+1) if len(set(S[i:i+K])) == K) if len(S) >= K else 0


def numKLenSubstrNoRepeats(self, S: str, K: int) -> int:
    ret = 0
    if len(S) < K: return 0
    for i in range(len(S)-K+1):

        ret += 1 if len(set(S[i:i+K])) == K else 0

        if len(set(S[i:i+K])) == K: ret += 1 

    return ret


def numKLenSubstrNoRepeats(self, S: str, K: int) -> int:
    start = 0
    end = K
    res = 0
    while end <= len(S):
        count = 0
        tmp_dict = defaultdict(int)
        for s in S[start:end]:
            if tmp_dict[s] == 0:
                count += 1
                tmp_dict[s] += 1
            elif tmp_dict[s] == 1:
                break
        if count == K:
            res += 1
        end += 1
        tmp_dict[start] -= 1
        start += 1
    return res






















