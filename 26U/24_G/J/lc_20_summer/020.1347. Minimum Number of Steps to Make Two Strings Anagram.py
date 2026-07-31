"""
020.1347. Minimum Number of Steps to Make Two Strings Anagram
生成每种字符都是奇数个的字符串

Given two equal-size strings s and t. In one step you can choose any character of t and replace it with another character.

Return the minimum number of steps to make t an anagram of s.

An Anagram of a string is a string that contains the same characters with a different (or the same) ordering.



Example 1:

Input: s = "bab", t = "aba"
Output: 1
Explanation: Replace the first 'a' in t with b, t = "bba" which is anagram of s.
Example 2:

Input: s = "leetcode", t = "practice"
Output: 5
Explanation: Replace 'p', 'r', 'a', 'i' and 'c' from t with proper characters to make t anagram of s.
Example 3:

Input: s = "anagram", t = "mangaar"
Output: 0
Explanation: "anagram" and "mangaar" are anagrams. 
Example 4:

Input: s = "xxyyzz", t = "xxyyzz"
Output: 0
Example 5:

Input: s = "friend", t = "family"
Output: 4
 

Constraints:

1 <= s.length <= 50000
s.length == t.length
s and t contain lower-case English letters only.

"""

def minSteps(self, s: str, t: str) -> int:
    cnt1, cnt2 = map(collections.Counter, (s, t))
    return sum(abs(cnt1[c] - cnt2[c]) for c in string.ascii_lowercase) // 2


def minSteps(self, s: str, t: str) -> int:
    cnt1, cnt2 = map(collections.Counter, (s, t))
    return sum((cnt1 - cnt2).values())
    
    return sum((collections.Counter(s) - collections.Counter(t)).values())

    return sum((v for _, v in (Counter(s)-Counter(t)).items()))

def minSteps(self, S: str, T: str) -> int:
    D = collections.Counter(S) - collections.Counter(T)
    return sum(max(0, D[s]) for s in set(S))

    for key in set(s) & set(t):
        s_count[key] = max(s_count[key] - t_count[key], 0)
    return sum(s_count.values())


def minSteps(self, s: str, t: str) -> int:
        count = collections.Counter(s)
        res = 0
        for c in t:
            if count[c] > 0:
                count[c] -= 1
            else:
                res += 1
        return res


def minSteps(self, s, t):
	count_s = collections.Counter(s)
	count_t = collections.Counter(t)
	res = 0

	for i in count_t:
		if i in count_s:
			if count_t[i] > count_s[i]:
				res += count_t[i] - count_s[i]
		else:
			res += count_t[i]
	return res

		

def minSteps(self, s, t):
    s_freq, t_freq, steps = defaultdict(int), defaultdict(int), 0
    for c in s:
        s_freq[c] += 1
    for c in t:
        t_freq[c] += 1
    for l in s_freq:
        s_i = s_freq[l] - t_freq[l]
        if s_i > 0:
            steps += s_i
    return steps


def minSteps(self, s: str, t: str) -> int:
    res = 0
    s = collections.Counter(s)
    t = collections.Counter(t)
    for c in string.ascii_lowercase:
        res += s[c] - t[c] if s[c] > t[c] else 0
    return res


def minSteps(self, s, t):
        res = 0
        c1 = Counter(s)
        c2 = Counter(t)
        for k,v in c2.items():
            if k not in c1:
                res += v
            else:
                if v > c1[k]:
                    res += v - c1[k]
        return res




def minSteps(self, s: str, t: str) -> int:
    res, freq = 0, [0] * 26  # lower-case English letters only
    for ch in s:
        freq[ord(ch) - ord('a')] += 1
    for ch in t:
        freq[ord(ch) - ord('a')] -= 1
        if freq[ord(ch) - ord('a')] < 0:
            res += 1
    return res


def minSteps(self, s: str, t: str) -> int:
    s_count = {val: s.count(val) for val in set(s)}
    t_count = {val: t.count(val) for val in set(t)}
    steps = 0
    for i in s_count:
        s_i = s_count.get(i, 0) - t_count.get(i, 0)
        if s_i > 0:
            steps += s_i
    return steps


def minSteps(self, s: str, t: str) -> int:
        cs = Counter(s)
        ct = Counter(t)
        val = 0
        for i in range(26):
            ch = chr(ord('a')+i)
            cnt_s = cs.get(ch, 0)
            cnt_t = ct.get(ch, 0)

            if cnt_s > cnt_t:
                val += (cnt_s - cnt_t)
        return val


def minSteps(self, s: str, t: str) -> int:
    x = collections.defaultdict(int)
    for ch in s:
        x[ch] += 1
    steps = 0
    for ch in t:
        if ch not in x:
            steps += 1
        else:
            if x[ch]:
                x[ch] -= 1
            else:
                steps += 1
    
    return steps








"""
给你一个整数 n，请你返回一个含 n 个字符的字符串，其中每种字符在该字符串中都恰好出现 奇数次 。

返回的字符串必须只含小写英文字母。如果存在多个满足题目要求的字符串，则返回其中任意一个即可。

 

示例 1：

输入：n = 4
输出："pppz"
解释："pppz" 是一个满足题目要求的字符串，因为 'p' 出现 3 次，且 'z' 出现 1 次。当然，还有很多其他字符串也满足题目要求，比如："ohhh" 和 "love"。
示例 2：

输入：n = 2
输出："xy"
解释："xy" 是一个满足题目要求的字符串，因为 'x' 和 'y' 各出现 1 次。当然，还有很多其他字符串也满足题目要求，比如："ag" 和 "ur"。
示例 3：

输入：n = 7
输出："holasss"

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/generate-a-string-with-characters-that-have-odd-counts
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。
"""
def generateTheString(self, n):
        
    if n % 2 == 1:
        return "a"*n
    else:
        return "a"*(n-1) + "b"

    return "a"*n if n%2==1 else "a"*(n-1) + "b"
    return "a"*n if n&1 else "a"*(n-1) + "b"

    return n % 2 and 'a' * n or 'a' + 'b' * (n - 1)

    return "a"*(n - 1) + ("a" if n&1 else "b");


def generateTheString(self, n: int) -> str:
    res = ""
    if n % 2 == 0:
        res += 'b'
        n -= 1
    while n:
        res += 'a'
        n -= 1
    return res


def generateTheString(self, n: int) -> str:
    str1=''
    if n%2!=0:
        for i in range(n):
            str1+='a'
    else:
        str1='a'
        for i in range(1,n):
            str1+='b'
    return str1 





























