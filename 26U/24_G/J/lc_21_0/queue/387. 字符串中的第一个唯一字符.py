# 387. 字符串中的第一个唯一字符
# 面试题50. 第一个只出现一次的字符

def firstUniqChar(self, s: str) -> str:
    q = deque()
    dc = dict()
    for i in range(len(s)):
        if s[i] not in dc:
            dc[s[i]] = i
            q.append(s[i])
        else:
            dc[s[i]] = -1
            while q and dc[q[0]] == -1:
                q.popleft()
    return q[0] if q else " "

        
def firstUniqChar(self, s: str) -> int:
    position = dict()
    q = collections.deque()
    n = len(s)
    for i, ch in enumerate(s):
        if ch not in position:
            position[ch] = i
            q.append((s[i], i))
        else:
            position[ch] = -1
            while q and position[q[0][0]] == -1:
                q.popleft()
    return -1 if not q else q[0][1]



def firstUniqChar(self, s: str) -> int:
    c = Counter(s)
    for i in range(len(s)):
        if c[s[i]] == 1:
            return i
    return -1


def firstUniqChar(self, s: str) -> int:
    position = dict()
    n = len(s)
    for i, ch in enumerate(s):
        if ch in position:
            position[ch] = -1
        else:
            position[ch] = i
    first = n
    for pos in position.values():
        if pos != -1 and pos < first:
            first = pos
    if first == n:
        first = -1
    return first








from collections import OrderedDict, Counter
class Solution:
    def firstUniqChar(self, s: str) -> int:
	    for i,j in OrderedDict(Counter(s)).items():
            if j == 1:
                return s.index(i)
        return -1


def firstUniqChar(self, s: str) -> int:
    visited = set()
    for i in range(len(s)):
        if s[i] not in visited:
            visited.add(s[i])
            if s.count(s[i]) == 1:
                return i
    return -1





