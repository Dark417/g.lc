"""
233.139. Word Break
单词拆分



Given a non-empty string s and a dictionary wordDict containing a list of non-empty 
words, determine if s can be segmented into a space-separated sequence of one or more dictionary words.

Note:

The same word in the dictionary may be reused multiple times in the segmentation.
You may assume the dictionary does not contain duplicate words.
Example 1:

Input: s = "leetcode", wordDict = ["leet", "code"]
Output: true
Explanation: Return true because "leetcode" can be segmented as "leet code".
Example 2:

Input: s = "applepenapple", wordDict = ["apple", "pen"]
Output: true
Explanation: Return true because "applepenapple" can be segmented as "apple pen apple".
             Note that you are allowed to reuse a dictionary word.
Example 3:

Input: s = "catsandog", wordDict = ["cats", "dog", "sand", "and", "cat"]
Output: false

https://leetcode-cn.com/problems/word-break/solution/shou-hui-tu-jie-san-chong-fang-fa-dfs-bfs-dong-tai/
"""

dp = [i == 0 for i in range(n+1)]


def wordBreak(self, s: str, wordDict: List[str]) -> bool:
	import functools
    @functools.lru_cache(None)
    def rec(s):
        if len(s) == 0:
            return True
        for word in wordDict:
            le = len(word)
            if s[:le] == word:
                if rec(s[le:]):
                    return True
        return False
    return rec(s)


def wordBreak(self, s, words):
    ok = [True]
    for i in range(1, len(s)+1):
        ok += any(ok[j] and s[j:i] in words for j in range(i)),
    return ok[-1]



def wordBreak(self, s: str, wordDict: List[str]) -> bool:       
    n=len(s)
    dp=[False]*(n+1)
    dp[0]=True
    for i in range(n):
        for j in range(i+1,n+1):
            if(dp[i] and (s[i:j] in wordDict)):
                dp[j]=True
    return dp[-1]



def wordBreak(self, s: str, wordDict: List[str]) -> bool:
    import functools
    @functools.lru_cache(None)
    def back_track(s):
        if(not s):
            return True
        res=False
        for i in range(1,len(s)+1):
            if(s[:i] in wordDict):
                res=back_track(s[i:]) or res
        return res
    return back_track(s)



# bfs
def wordBreak(self, s: str, wordDict: List[str]) -> bool:
    from collections import deque
		q = deque([s])
	seen = set() 
	while q:
        s = q.popleft()    # popleft() = BFS ; pop() = DFS
        for word in wordDict:
            if s.startswith(word):
                new_s = s[len(word):]
				if new_s == "": 
                    return True
                if new_s not in seen:
                    q.append(new_s)
                    seen.add(new_s)
    return False



def wordBreak(self, s, wordDict):
    queue = [0]
    slen = len(s)
    lenList = [l for l in set(map(len,wordDict))]
    visited = [0 for _ in range(0, slen + 1)]
    while queue:
        tmpqueue = []
        for start in queue:
            for l in lenList:
                if s[start:start+l] in wordDict:
                    if start + l == slen:
                        return True
                    if visited[start + l] == 0:
                        tmpqueue.append(start+l)
                        visited[start + l] = 1
        queue, tmpqueue = tmpqueue, []
    return False




def word_break(s, words):
 	d = [False] * len(s)    
 	for i in range(len(s)):
 		for w in words:
 			if w == s[i-len(w)+1:i+1] and (d[i-len(w)] or i-len(w) == -1):
 				d[i] = True
 	return d[-1]


# improved
def wordBreak(self, s, wordDict):
    n = len(s)
    dp = [False for i in range(n+1)]//*Changed*
    dp[0] = True
    for i in range(1,n+1):
        for w in wordDict:
            if dp[i-len(w)] and s[i-len(w):i]==w://*Changed*
                dp[i]=True
    return dp[-1]





# trie
class TrieNode(object):
    def __init__(self, char=None, isWord=False):
        self.char = char
        self.isWord = isWord
        self.children = {}


class Trie(object):
    def __init__(self):
        self.root = TrieNode()
        self.cache = {}

    def insert(self, word):
        root = self.root
        for char in word:
            if char not in root.children:
                root.children[char] = TrieNode(char)
            root = root.children[char]
        root.isWord = True

    def cache(f):
        def method(obj, s):
            if s not in obj.cache:
                obj.cache[s] = f(obj, s)
            return obj.cache[s]
        return method

    @cache
    def search(self, s):
        root = self.root
        for i, char in enumerate(s):
            if char not in root.children:
                return False

            if root.children[char].isWord:
                if self.search(s[i + 1:]):
                    return True
            root = root.children[char]
        return root.isWord


class Solution(object):
    def wordBreak(self, s, wordDict):
        trie = Trie()
        [trie.insert(word) for word in wordDict]

        return trie.search(s)

# +
def createTrie(words):
    def _createTrie(): return collections.defaultdict(_createTrie)

    t = _createTrie()
    for word in words:
        root = t
        for w in word:
            root = root[w]
        root['#']
    return t

class Solution(object):    
    def wordBreak(self, s, wordDict):   
        def search(t,s):
            root = t
            
            for i,c in enumerate(s):
                if c not in t:
                    return False
                else:
                    if '#' in t[c] and search(root, s[i+1:]):
                        return True
                    t = t[c]

            return '#' in t       
        
        t = createTrie(wordDict)
        return search(t, s)





















































