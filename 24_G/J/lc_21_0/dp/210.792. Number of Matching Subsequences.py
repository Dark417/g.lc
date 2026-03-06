"""
210.792. Number of Matching Subsequences
匹配子序列的单词数



Given string S and a dictionary of words words, find the number of words[i] that is a subsequence of S.

Example :
Input: 
S = "abcde"
words = ["a", "bb", "acd", "ace"]
Output: 3
Explanation: There are three words in words that are a subsequence of S: "a", "acd", "ace".
Note:

All words in words and S will only consists of lowercase letters.
The length of S will be in the range of [1, 50000].
The length of words will be in the range of [1, 5000].
The length of words[i] will be in the range of [1, 50].



"""



def numMatchingSubseq(self, S: str, words: List[str]) -> int:
    def issub(t):
        i = 0
        for c in S: 
            if i < len(t) and t[i] == c: i += 1
        return i == len(t)

    return sum(map(issub, words))
    return sum(1 for i in words if issub(i))






# Stefan
def numMatchingSubseq(self, S, words):
    waiting = collections.defaultdict(list)
    for w in words:
        waiting[w[0]].append(iter(w[1:]))
    for c in S:
        for it in waiting.pop(c, ()):
            waiting[next(it, None)].append(it)
    return len(waiting[None])



def numMatchingSubseq(self, S, words):
    waiting = collections.defaultdict(list)
    for it in map(iter, words):
        waiting[next(it)].append(it)
    for c in S:
        for it in waiting.pop(c, ()):
            waiting[next(it, None)].append(it)
    return len(waiting[None])



def numMatchingSubseq(self, S, words):
    waiting = collections.defaultdict(list, {' ': map(iter, words)})
    for c in ' ' + S:
        for it in waiting.pop(c, ()):
            waiting[next(it, None)].append(it)
    return len(waiting[None])





def numMatchingSubseq(self, S, words):
    word_dict = defaultdict(list)
    count = 0
    
    for word in words:
        word_dict[word[0]].append(word)            
    
    for char in S:
        words_expecting_char = word_dict[char]
        word_dict[char] = []
        for word in words_expecting_char:
            if len(word) == 1:
                # Finished subsequence! 
                count += 1
            else:
                word_dict[word[1]].append(word[1:])
    
    return count




def numMatchingSubseq(self, S: str, words: List[str]) -> int:
    heads = collections.defaultdict(list)
    for w in words:
        heads[w[0]].append(iter(w[1:]))
    for c in S:
        if c in heads:
            for itr in heads.pop(c):
                heads[next(itr, None)].append(itr)
    return len(heads[None])





def numMatchingSubseq(self, S, words):
    needs = defaultdict(list)
    for word in words:
        needs[word[0]].append((0, word))
    matches = 0
    for c in S:
        met_needs = needs[c]
        needs[c] = []
        for i, w in met_needs:
            if i+1 >= len(w):
                matches += 1
                continue
            needs[w[i+1]].append((i+1, w))
    return matches





def numMatchingSubseq(self, S, words):
    from collections import Counter
    count = 0
    words = Counter(words)
    for word,num in words.items():
        start = 0
        flag = False
        for alp in word:
            start = S.find(alp,start) + 1
            if start == 0:
                flag = True
                break
        if not flag:
            count += num
    return count




def numMatchingSubseq(self, S, words):
    def check(s, i):
        for c in s:
            i = S.find(c, i) + 1
            if not i: return False
        return True
    return sum((check(word, 0) for word in words))






def is_subseq(word, i):
	for char in word:
		i = S.find(char, i) + 1
		if not i:
			return False
		return True

    result = 0
    positive = set()
    negative = set()
    
    for word in words:
        if word not in positive and word not in negative:
            if is_subseq(word, 0):
                positive.add(word)
                result += 1
            else:
                negative.add(word)
        elif word in positive:
            result += 1
    
    return result







def numMatchingSubseq(self, S: str, words: List[str]) -> int:
    count=0
    for w in words:
        i=0
        j=0
        while(j<len(w) and i<len(S)):
            if w[j]== S[i]:
                j+=1
                i+=1
            else:
                i+=1
        if j== len(w):
            count+=1
    return count


def numMatchingSubseq(self, S: str, words: List[str]) -> int:
    count=0
    indexes= collections.defaultdict(list)
    
    for i,c in enumerate(S):
        indexes[c].append(i)
    
    for w in words:
        minim=-1
        for c in w:
            if c not in indexes:
                minim=-1
                break
            for i in indexes[c]:
                found= False
                if i> minim:
                    minim= i
                    found=True
                    break
            if not found:
                minim=-1
                break
        if minim!= -1:
            count+=1
            
    return count


def numMatchingSubseq(self, S: str, words: List[str]) -> int:
    count = 0
    needed = collections.defaultdict(list)
    
    for w in words:
        needed[w[0]].append((1, w))
    
    for c in S:
        if c in needed:
            nextUps= needed[c]
            del needed[c]
            for i,w in nextUps:
                if i== len(w):
                    count+=1
                else:
                    needed[w[i]].append((i+1, w))
    return count



def numMatchingSubseq(self, S: str, words: List[str]) -> int:
	cnt = collections.Counter(words) # remove duplicates
    return sum([cnt[word] for word in cnt if self.isSubseq(word, S)])

# check whether s is a subsequence of t
def isSubseq(self, s, t):
	i = 0
	for c in s:
		i = t.find(c, i) + 1
		if not i: return False
	return True



# binary
# O(len(words) * avg_word_length * log(len(S))



def numMatchingSubseq(self, S, words):
    def isMatch(word, w_i, d_i):
        if w_i == len(word): return True
        l = dict_idxs[word[w_i]]
        if len(l) == 0 or d_i > l[-1]: return False
        i = l[bisect_left(l, d_i)]
        return isMatch(word, w_i + 1, i + 1)

    dict_idxs = defaultdict(list)
    for i in range(len(S)):
        dict_idxs[S[i]].append(i)
    return sum(isMatch(word, 0, 0) for word in words)



def numMatchingSubseq(self, S: str, words: List[str]) -> int:
    def isSubseq(word):
        prev = -1
        for c in word:
            if c not in lookup: return False
            index = bisect.bisect(lookup[c], prev)
            if index >= len(lookup[c]): return False
            prev = lookup[c][index]
        return True

    lookup = collections.defaultdict(list)
    for i, c in enumerate(S):
        lookup[c].append(i)
    return sum([1 for word in words if isSubseq(word)])



def numMatchingSubseq(self, S: str, words: List[str]) -> int:
    def isValid(word, indexMap):
        i = -1
        for c in word:
            index = ord(c) - ord('a')
            j = bisect.bisect_left(indexMap[index], i+1)
            if j == len(indexMap[index]): return False
            i = indexMap[index][j]
        return True
    
    m = [[] for _ in range(26)]
    for i in range(len(S)):
        m[ord(S[i]) - ord('a')].append(i)
    return sum(isValid(word, m) for word in words)


def contains(self,word,dic):
    index = -1
    for char in word:
        if char in dic:
            ls = dic[char]
            i = bisect.bisect_right(ls,index)
            if i < len(ls):
                index  = ls[i]
            else:
                return False
        else:
            return False
    return True


def numMatchingSubseq(self, S, words):
    # build a dic that store index of string in order
    dic = {}
    for index,char in enumerate(S):
        if char in dic:
            dic[char].append(index)
        else:
            dic[char] = [index]

    count = 0
    for word in words:
        count += self.contains(word,dic)
    return count




def numMatchingSubseq(self, S: str, words: List[str]) -> int:
    d = collections.defaultdict(list)
    for i, ch in enumerate(S):
        d[ch].append(i)
        
    c = 0
    for word in words:
        if len(word) > len(S) or len(word) == 0:
            continue
        
        last  = 0
        flag = True
        for ch in word:
            if ch not in d:
                flag = False
                break
            i = bisect_left(d[ch], last)
            # print(ch, i, last)
            if i >= len(d[ch]):
                flag = False
                break
            
            last = d[ch][i] + 1
        
        if flag:
            # print(word)
            c += 1
    return c




from collections import defaultdict
from bisect import bisect_right
def numMatchingSubseq(self, S: str, words: List[str]) -> int:
    d = defaultdict(list)

    # Record all the occurrences of the individual characters 
    for i, x in enumerate(S):
        d[x].append(i)

    cnt = 0
    for word in words:
        ptr = -1
        for c in word:
            if not d[c] or ptr >= d[c][-1]: # Check whether there's a character 'c' existing after current position 'ptr' in S
                ptr = len(S)
            else:
                idx = bisect_right(d[c], ptr) 
                ptr = d[c][idx] # Update the current position

        if ptr < len(S):
            cnt += 1

    return cnt





















