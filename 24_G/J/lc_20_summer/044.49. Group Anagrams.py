"""
044.49. Group Anagrams
字母异位词分组


Given an array of strings, group anagrams together.

Example:

Input: ["eat", "tea", "tan", "ate", "nat", "bat"],
Output:
[
  ["ate","eat","tea"],
  ["nat","tan"],
  ["bat"]
]
Note:

All inputs will be in lowercase.
The order of your output does not matter.

"""


def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
    ret = []
    dic = {}
    for w in strs:
        srt = "".join(sorted(w))
        if srt not in dic:
            dic[srt] = []
        dic[srt].append(w)
    
    ret += [i for i in dic.values()]
    # for v in dic.values():
    #         ret.append(v)
    return ret

    # if key in dic:
    #     dic.get(key).append( str )
    # else:
    #     dic[key] = [str]


    from collections import defaultdict
    lookup = defaultdict(list)


def anagrams(self, strs):
    count = collections.Counter([tuple(sorted(s)) for s in strs])
    return filter(lambda x: count[tuple(sorted(x))]>1, strs)

#py1
def groupAnagrams(self, strs):
	return [sorted(g) for _, g in itertools.groupby(sorted(strs, key=sorted), sorted)]

	groups = itertools.groupby(sorted(strs, key=sorted), sorted)
	return [sorted(members) for _, members in groups]

#py2
def groupAnagrams(self, strs):
    groups = collections.defaultdict(list)
    for s in strs:
        groups[tuple(sorted(s))].append(s)
    return map(sorted, groups.values())



def groupAnagrams(self, strs):
    matches = dict()
    [matches.setdefault("".join(sorted(s)), []).append(s) for s in strs]
    return matches.values()


def groupAnagrams(self, strs):
    d = {}
    for w in sorted(strs):
    #for w in strs:
        key = tuple(sorted(w))
        d[key] = d.get(key, []) + [w]
    return list(d.values())
    #return sorted(d.values())


def groupAnagrams(self, strs):
    ans = collections.defaultdict(list)
    for s in strs:
        ans[tuple(sorted(s))].append(s)
    return ans.values()



def groupAnagrams(strs):
    ans = collections.defaultdict(list)
    for s in strs:
        count = [0] * 26
        for c in s:
            count[ord(c) - ord('a')] += 1
        ans[tuple(count)].append(s)
    return ans.values()

	anagrams = defaultdict(list)
    for word in strs:
        anagrams[''.join(sorted(word))].append(word)
    return list(anagrams)


def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
    dic = {}
    res =[]
    for i in strs:
        dic.setdefault(str(sorted(i)),[]).append(i)
    for value in dic.values():
        res.append(value)
    return res


def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
    from collections import defaultdict
    prime = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103]
    lookup = defaultdict(list)
    for _str in strs:
        key_val = 1
        for s in _str:
            key_val *= prime[ord(s) - 97]
        lookup[key_val].append(_str)
    return list(lookup.values())





# z
def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        
    mapx = dict()
    for i in strs:
        tmp = ''.join(sorted(list(i)))
        if tmp in mapx.keys():
            mapx[tmp].append(i)
        else:
            mapx[tmp] = [i]
    return list(mapx.values())













