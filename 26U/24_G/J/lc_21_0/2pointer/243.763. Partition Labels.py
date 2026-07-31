"""
243.763. Partition Labels
划分字母区间

A string S of lowercase English letters is given. We want to partition this string 
into as many parts as possible so that each letter appears in at most one part, 
and return a list of integers representing the size of these parts.

 

Example 1:

Input: S = "ababcbacadefegdehijhklij"
Output: [9,7,8]
Explanation:
The partition is "ababcbaca", "defegde", "hijhklij".
This is a partition so that each letter appears in at most one part.
A partition like "ababcbacadefegde", "hijhklij" is incorrect, because it splits S into less parts.
 

Note:

S will have length in range [1, 500].
S will consist of lowercase English letters ('a' to 'z') only.

"""

def partitionLabels(self, S):
    last = {c: i for i, c in enumerate(S)}
    j = anchor = 0
    ans = []
    for i, c in enumerate(S):
        j = max(j, last[c])
        if i == j:
            ans.append(i - anchor + 1)
            anchor = i + 1
        
    return ans


def partitionLabels(self, S):
    sizes = []
    while S:
        i = 1
        while set(S[:i]) & set(S[i:]):
            i += 1
        sizes.append(i)
        S = S[i:]
    return sizes



def partitionLabels(self, S):
    cuts = [i for i in range(len(S)+1) if not set(S[:i]) & set(S[i:])]
    return [j - i for i, j in zip(cuts, cuts[1:])]


def partitionLabels(self, S):
    cuts = [i for i in range(len(S)+1) if set(S[:i]).isdisjoint(S[i:])]
    return [j - i for i, j in zip(cuts, cuts[1:])]





def partitionLabels(self, S):
    result, last_seen, max_last_seen, count = [], {}, 0, 0
    for i, char in enumerate(S):
        last_seen[char] = i
    for i, char in enumerate(S):
        max_last_seen = max(max_last_seen, last_seen[char])
        count += 1
        if i == max_last_seen:
            result.append(count)
            count = 0
    return result


    dic = {}
    for i, c in enumerate(S):
        dic[c] = i
    
    cur_max = 0
    res = []
    count = 0
    
    for i, c in enumerate(S):
        count += 1
        cur_max = max(cur_max, dic[c])
        
        if cur_max == i:
            res.append(count)
            count = 0
    return res



def partitionLabels(self, S):
    results = []
    last = {}
    
    for i in range(len(S)-1,-1,-1):
        if S[i] not in last:
            last[S[i]] = i
    
    i = 0
    span = 0
    while i < len(S):
        j = last[S[i]]
        span = 1
        while i != j:
            i += 1
            span += 1
            j = max(j,last[S[i]])
        results.append(span)
        i += 1
        
    return results





def partitionLabels(self, S: str) -> List[int]:
    res = []
    st = {}
    for i, c in enumerate(S):
        if c not in st:
            st[c] = [i]
        st[c].append(i)
    i = j = p = 0
    while i < len(S):
        if len(st[S[i]]) == 1:
            res.append(1)
            i += 1
            continue
        mx = st[S[i]][-1]
        for j in range(i+1, mx):
            mx = max(mx, st[S[j]][-1])
        res.append(mx - res[-1] if res else mx)
        i = mx
        if i == len(S)-1:
            break
    return res










































































