# 438. 找到字符串中所有字母异位词


def findAnagrams(self, s, p):
    res = []
    pCounter = Counter(p)
    sCounter = Counter(s[:len(p)-1])
    for i in range(len(p)-1,len(s)):
        sCounter[s[i]] += 1   # include a new char in the window
        if sCounter == pCounter:    # This step is O(1), since there are at most 26 English letters 
            res.append(i-len(p)+1)   # append the starting index
        sCounter[s[i-len(p)+1]] -= 1   # decrease the count of oldest char in the window
        if sCounter[s[i-len(p)+1]] == 0:
            del sCounter[s[i-len(p)+1]]   # remove the count if it is 0
    return res



def findAnagrams(self, s: str, p: str) -> List[int]:
    myDictP=collections.Counter(p)
    myDictS=collections.Counter(s[:len(p)])
    output=[]
    i=0
    j=len(p)
    while j<=len(s):
        if myDictS==myDictP:
            output.append(i)
        myDictS[s[i]]-=1
        if myDictS[s[i]]<=0:
            myDictS.pop(s[i])
        if j<len(s):    
             myDictS[s[j]]+=1
        j+=1
        i+=1
    return output



def findAnagrams(self, s: str, p: str) -> List[int]:
	LS, LP, S, P, A = len(s), len(p), 0, 0, []
	if LP > LS: return []
	for i in range(LP): S, P = S + hash(s[i]), P + hash(p[i])
	if S == P: A.append(0)
	for i in range(LP, LS):
		S += hash(s[i]) - hash(s[i-LP])
		if S == P: A.append(i-LP+1)
	return A



def findAnagrams(self, s: str, p: str) -> List[int]:
    if len(p) > len(s): return []
    result = []
    hashOfP = sum(hash(l) for l in p)
    currentHash = 0
    for l in s[:len(p)]:
        currentHash += hash(l)
    if currentHash == hashOfP: result.append(0)
    for i, l in enumerate(s[len(p):]):
        currentHash += hash(l) - hash(s[i])
        if currentHash == hashOfP:
            result.append(i+1)
    return result




def findAnagrams(self, s: str, p: str) -> List[int]:
    indices = []
    length_p = len(p)
    if length_p > len(s):
        return []
	counter_p = [0] * 26
    for c in p:
		counter_p[ord(c) - 97] += 1
    counter = [0] * 26
    for i in range(length_p - 1):
        counter[ord(s[i]) - 97] += 1
	for i, c in enumerate(s[length_p - 1:]):
        counter[ord(c) - 97] += 1
        if counter_p == counter:
            indices.append(i)
        counter[ord(s[i]) - 97] -= 1
    return indices




def findAnagrams(self, s: str, p: str) -> List[int]:
    res = []
    if len(p) > len(s):     
        return res
    dic = {}
    m = len(p)
    count = m
    for i in range(m):
        dic[p[i]] = dic.get(p[i], 0) +1   #记录所需元素及个数
    i = 0
    while i < len(s):
        if s[i] in dic:              
            dic[s[i]] -= 1               #如果S[i]在dic中存在，更新值
            if dic[s[i]] >= 0:           #如果dic[s[i]]<0,表明不需要这个数，不能更新count
                count -= 1
        if i >= m:                       # 当i>=m, 弹出失效的字符，保证长度相等
            if s[i-m] in dic:
                dic[s[i-m]] += 1        #s[i-m]未必一定在dic中，需要判断
                if dic[s[i-m]] > 0:     #需要的数被弹出，更新count
                    count += 1
        if count == 0:
            res.append(i-m+1)
        i += 1
    return res








