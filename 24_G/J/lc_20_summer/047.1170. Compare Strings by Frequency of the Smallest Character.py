"""
047.1170. Compare Strings by Frequency of the Smallest Character
比较字符串最小字母出现频次


Let's define a function f(s) over a non-empty string s, 
which calculates the frequency of the smallest character in s. 
For example, if s = "dcce" then f(s) = 2 because the smallest character is "c" and its frequency is 2.

Now, given string arrays queries and words, 
return an integer array answer, where each answer[i] is the number of 
words such that f(queries[i]) < f(W), where W is a word in words.

 

Example 1:

Input: queries = ["cbd"], words = ["zaaaz"]
Output: [1]
Explanation: On the first query we have f("cbd") = 1, f("zaaaz") = 3 so f("cbd") < f("zaaaz").
Example 2:

Input: queries = ["bbb","cc"], words = ["a","aa","aaa","aaaa"]
Output: [1,2]
Explanation: On the first query only f("bbb") < f("aaaa"). 
On the second query both f("aaa") and f("aaaa") are both > f("cc").
 

Constraints:

1 <= queries.length <= 2000
1 <= words.length <= 2000
1 <= queries[i].length, words[i].length <= 10
queries[i][j], words[i][j] are English lowercase letters.

"""

def numSmallerByFrequency(self, queries: List[str], words: List[str]) -> List[int]:
    ret, f = [], []
    for word in words:
        w = "".join(sorted(word))
        f.append(w.count(w[0]))
    for i in range(len(queries)):
        w = "".join(sorted(queries[i]))
        fq = w.count(w[0])
        ret.append(sum(1 for k in f if k > fq ))
        ret.append(len([k for k in f if fq < k]))
    return ret


def numSmallerByFrequency(self, queries: List[str], words: List[str]) -> List[int]:
	f = sorted(w.count(min(w)) for w in words)
    return [len(f) - bisect.bisect(f, q.count(min(q))) for q in queries]

    words_freq = sorted([word.count(min(word)) for word in words])
    return [len(words) - bisect(words_freq, query.count(min(query))) for query in queries]


def numSmallerByFrequency(self, queries: List[str], words: List[str]) -> List[int]:
    f = lambda word: word.count(min(word))
    words = sorted(map(f, words))
    return [len(words) - bisect(words, f(query)) for query in queries]






def numSmallerByFrequency(self, queries: List[str], words: List[str]) -> List[int]:
    # 1. Capture counts of smallest characters in each word, and sort 
    # the list in ascending order.
    W = sorted([w.count(min(w)) for w in words])
    
    res = []
    for q in queries:
        # 2. Perform binary search of smallest characters in each query
        # against the sorted list from step#1.
        cnt = q.count(min(q))
        idx = bisect.bisect(W, cnt)
        res.append(len(words) - idx)
    return res



def numSmallerByFrequency(self, queries: List[str], words: List[str]) -> List[int]:
    f = lambda s: s.count(min(s))
    l, wlst = len(words), [f(word) for word in words]
    biggerthan, m = [0] * 11, [0] * 11
    for i in wlst: m[i] += 1
    #compute a list contain bigger than frequence occurence
    for i in range(1, 11): 
        m[i] += m[i-1]
        biggerthan[i] = l - m[i]
    return [biggerthan[f(i)] for i in queries]


def numSmallerByFrequency(self, queries: List[str], words: List[str]) -> List[int]:
    f = lambda s: s.count(min(s))
    l, wlst = len(words), [f(word) for word in words]
    m = [0] * 11
    for i in wlst: m[i] += 1
    m = [l - i for i in itertools.accumulate(m)]
    return [m[f(i)] for i in queries]


def numSmallerByFrequency(self, queries, words):
	from collections import Counter
    queries_list = []
    words_list = []
    results = []
    for query in queries:
        queries_list.append(Counter(query)[min(query)])
    for word in words:
        words_list.append(Counter(word)[min(word)])
    words_list = sorted(words_list)
    
    def find_word_freq(query_fre):
        ans = 0
        l = 0
        r = len(words_list) - 1
        count = 0
        while (l <= r):
            mid = (l + r) // 2
            if words_list[mid] <= query_fre:
                l = mid + 1
            elif words_list[mid] > query_fre:
                r = mid - 1         
        return len(words_list) - l
            
    for query in queries_list:
        results.append(find_word_freq(query))
    print(queries_list, words_list, results)
    return (results)


def numSmallerByFrequency(self, queries: List[str], words: List[str]) -> List[int]:
	def f(s):
		t = sorted(list(s))[0]
		return s.count(t)
	query = [f(x) for x in queries]
	word = [f(x) for x in words]
	m = []
	for x in query:
		count = 0
		for y in word:
			if y>x:
				count+=1
		m.append(count)
	return m

def numSmallerByFrequency(self, queries: List[str], words: List[str]) -> List[int]:
    #upper bound binary search
    def bs_right(lst, target):
        #r = len(lst) - 1 is wrong, it will return len(lst) - 1 when target > lst[-1] while it should return len(lst)
        l, r = 0, len(lst)
        while l < r:
            mid = l + (r - l) // 2
            if lst[mid] <= target: l = mid + 1
            else: r = mid
        return l
            
    f = lambda s: s.count(min(s))
    l, wlst = len(words), [f(word) for word in words]
    wlst.sort()
    return [l - bs_right(wlst, f(i)) for i in queries]


def numSmallerByFrequency(self, queries, words):
    a = [x.count(min(x)) for x in queries]
    b = [word.count(min(word)) for word in words]

    b.sort()
    def get_index(lst,ele):
        n = len(lst)
        if n==0:
            return 0
        elif n==1:
            return 1*(ele<lst[0])
        else:
            mid = len(lst)//2
            if ele >= lst[mid]:
                return get_index(lst[mid+1:],ele)
            else:
                return (n-mid)+get_index(lst[:mid],ele)

    return [get_index(b,ele) for ele in a]



def count(self,word):
    alpha = 'abcdefghijklmnopqrstuvwxyz'
    for i in alpha:
        if i in word:
            return word.count(i)

def wordnum(self,wcount,wordscount):
    n = 0 
    for i in wordscount:
        if i > wcount:
            n += 1
    return n

def numSmallerByFrequency(self, queries: List[str], words: List[str]) -> List[int]:
    res = []
    wordscount = []
    l = len(words)
    for w in words:
        wordscount.append(self.count(w))
        
        
    for w in queries:
        wcount = self.count(w)
        res.append(self.wordnum(wcount,wordscount))
    
    return res













