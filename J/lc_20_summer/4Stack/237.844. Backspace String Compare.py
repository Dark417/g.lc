"""
237.844. Backspace String Compare
比较含退格的字符串

Given two strings S and T, return if they are equal when both are typed into empty text editors. # means a backspace character.

Note that after backspacing an empty text, the text will continue empty.

Example 1:

Input: S = "ab#c", T = "ad#c"
Output: true
Explanation: Both S and T become "ac".
Example 2:

Input: S = "ab##", T = "c#d#
"Output: true
Explanation: Both S and T become "".
Example 3:

Input: S = "a##c", T = "#a#c"
Output: true
Explanation: Both S and T become "c".
Example 4:

Input: S = "a#c", T = "b"
Output: false
Explanation: S becomes "c" while T becomes "b".
Note:

1 <= S.length <= 200
1 <= T.length <= 200
S and T only contain lowercase letters and '#' characters.
Follow up:

Can you solve it in O(N) time and O(1) space?


"""


def backspaceCompare(self, S, T):
    def back(res, c):
        if c != '#': res.append(c)
        elif res: res.pop()
        return res
    return reduce(back, S, []) == reduce(back, T, [])



def backspaceCompare(self, S, T):
    i, j = len(S) - 1, len(T) - 1
    backS = backT = 0
    while True:
        while i >= 0 and (backS or S[i] == '#'):
            backS += 1 if S[i] == '#' else -1
            i -= 1
        while j >= 0 and (backT or T[j] == '#'):
            backT += 1 if T[j] == '#' else -1
            j -= 1
        if not (i >= 0 and j >= 0 and S[i] == T[j]):
            return i == j == -1
        i, j = i - 1, j - 1



def backspaceCompare(self, S, T):
    back = lambda res, c: res[:-1] if c == '#' else res + c
    return reduce(back, S, "") == reduce(back, T, "")




def backspaceCompare(self, S: str, T: str) -> bool:
	s, t = [], []
	for i in S: s = s + [i] if i != '#' else s[:-1]
	for i in T: t = t + [i] if i != '#' else t[:-1]
	return s == t



def backspaceCompare(self, S: str, T: str) -> bool:
	a, A = [[],[],0,0], [S,T]
	for i in range(2):
		for j in A[i][::-1]:
			if j != '#':
				if a[i+2] == 0: a[i].append(j)
				else: a[i+2] -= 1
			else: a[i+2] += 1
	return a[0] == a[1]



def backspaceCompare(self, S1, S2):
    r1 = len(S1) - 1 
    r2 = len (S2) - 1
    
    while r1 >= 0 or r2 >= 0:
        char1 = char2 = ""
        if r1 >= 0:
            char1, r1 = self.getChar(S1, r1)
        if r2 >= 0:
            char2, r2 = self.getChar(S2, r2)
        if char1 != char2:
            return False
    return True
    

def getChar(self, s , r):
    char, count = '', 0
    while r >= 0 and not char:
        if s[r] == '#':
            count += 1
        elif count == 0:
            char = s[r]
        else:
            count -= 1
        r -= 1
    return char, r




def backspaceCompare(self, S: str, T: str) -> bool:
    def next(i: int, S: str) -> int:
        backCnt = 0
        while i >= 0 and (S[i] == '#' or backCnt > 0):
            backCnt += 1 if S[i] == '#' else -1
            i -= 1
        return i
    
    i, j = len(S) - 1, len(T) - 1
    while i >= 0 or j >= 0:
        i, j = next(i, S), next(j, T)
        if i >= 0 and j >= 0 and S[i] == T[j]:
            i -= 1
            j -= 1
        else:
            return i == -1 == j
    return True





def backspaceCompare(self, S: str, T: str) -> bool:
    cts, ctt, rs, rt = 0, 0, len(S) - 1, len(T) - 1
    while rs >= 0 or rt >= 0:
        while rs >= 0 and (S[rs] == '#' or cts): 
            if S[rs] == '#': cts += 1
            else: cts -= 1
            rs -= 1
        while rt >= 0 and (T[rt] == '#' or ctt): 
            if T[rt] == '#': ctt += 1
            else: ctt -= 1
            rt -= 1
        if S[rs] != T[rt]: return False
        rs, rt = rs-1, rt-1
    return True









def backspaceCompare(self, S, T):
    def build(S):
        ans = []
        for c in S:
            if c != '#':
                ans.append(c)
            elif ans:
                ans.pop()
        return "".join(ans)
    return build(S) == build(T)


    def bsString(string):
        res = []
        for c in string:
            if c != '#':
                res.append(c)
            else:
                res = res[:-1]
        return res




def backspaceCompare(self, S, T):
    def F(S):
        skip = 0
        for x in reversed(S):
            if x == '#':
                skip += 1
            elif skip:
                skip -= 1
            else:
                yield x

    return all(x == y for x, y in itertools.izip_longest(F(S), F(T)))










def backspaceCompare(self, S: str, T: str) -> bool:
    s1, s2 = [], []
    for i in S:
        if i == "#":
            if s1 == []:
                continue
            else:
                s1.pop()
        else:
            s1.append(i)
    for i in T:
        if i == "#":
            if s2 == []:
                continue
            else:
                s2.pop()
        else:
            s2.append(i)
    return s1 == s2













































































