# 205. 同构字符串


return all(map({}.setdefault, a, b) == list(b) for a, b in ((s, t), (t, s)))


return len(set(zip(s, t))) == len(set(s)) == len(set(t))

return len(set(zip(s, t))) == len(set(s)) and len(set(zip(t, s))) == len(set(t))

return [s.find(i) for i in s] == [t.find(j) for j in t]

return map(s.find, s) == map(t.find, t)

return [*map(s.index, s)] == [*map(t.index, t)]




def isIsomorphic(self, s: str, t: str) -> bool:
	s2t, t2s = {}, {}
	for i in range(len(s)):
		if s[i] in s2t and s2t[s[i]] != t[i] or t[i] in t2s and t2s[t[i]] != s[i]:
			return False
		s2t[s[i]] = t[i]
		t2s[t[i]] = s[i]
	return True


def isIsomorphic(self, s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    dc, fs = {}, {}
    for i in range(len(s)):
        if s[i] not in dc:
            dc[s[i]] = []
        dc[s[i]].append(i)
    for i in range(len(t)):
        if t[i] not in fs:
            fs[t[i]] = []
        fs[t[i]].append(i)
    return [dc[i] for i in dc] == [fs[i] for i in fs]



def isIsomorphic1(self, s, t):
    d1, d2 = {}, {}
    for i, val in enumerate(s):
        d1[val] = d1.get(val, []) + [i]
    for i, val in enumerate(t):
        d2[val] = d2.get(val, []) + [i]
    return sorted(d1.values()) == sorted(d2.values())


    
def isIsomorphic2(self, s, t):
    d1, d2 = [[] for _ in xrange(256)], [[] for _ in xrange(256)]
    for i, val in enumerate(s):
        d1[ord(val)].append(i)
    for i, val in enumerate(t):
        d2[ord(val)].append(i)
    return sorted(d1) == sorted(d2)


def isIsomorphic6(self, s, t):
    d1, d2 = [0 for _ in xrange(256)], [0 for _ in xrange(256)]
    for i in xrange(len(s)):
        if d1[ord(s[i])] != d2[ord(t[i])]:
            return False
        d1[ord(s[i])] = i+1
        d2[ord(t[i])] = i+1
    return True






