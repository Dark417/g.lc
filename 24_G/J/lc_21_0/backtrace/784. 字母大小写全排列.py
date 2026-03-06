"""
079.784. Letter Case Permutation
字母大小写全排列

Given a string S, we can transform every letter individually to be lowercase or uppercase
 to create another string.  Return a list of all possible strings we could create.

Examples:
Input: S = "a1b2"
Output: ["a1b2", "a1B2", "A1b2", "A1B2"]

Input: S = "3z4"
Output: ["3z4", "3Z4"]

Input: S = "12345"
Output: ["12345"]




"""

# D
def letterCasePermutation(self, S: str) -> List[str]:
    res = []
    l = list(S)
    cidx = []
    iidx = []

    for i, c in enumerate(l):
        if c.isalpha()
            cidx.append(i)
        else:
            sidx.append(i)

    length = len(cidx)
    def dfs(length, ):

    for n in range(len(cidx)):
        tmp = []
        x = []
        dfs(n, [])

        for i in range(len(S)):
            if i in iidx:
                x.append(S[i])
            else:
                if c[i] == c[i].lower():
                    x.append(c[i].upper())
                else:
                    x.append(c[i].lower)
    res.append("".join(x))
    return res



# lee
def letterCasePermutation(self, S):
    L = [[i.lower(), i.upper()] if i.isalpha() else i for i in S]
    return [''.join(i) for i in itertools.product(*L)]

	return [''.join(w) for w in product(*(set((i.lower(), i.upper())) for i in S))]
	return reduce(lambda x, y: [word + ch for word in x for ch in set([y.lower(), y.upper()])], S, [""])



def letterCasePermutation(self, S):
    res = ['']
    for ch in S:
        if ch.isalpha():
            res = [i+j for i in res for j in [ch.upper(), ch.lower()]]
        else:
            res = [i+ch for i in res]
    return res



def letterCasePermutation(self, S):
    res = [S]
    for i, c in enumerate(S):
        if c.isalpha():
            res.extend([s[:i] + s[i].swapcase() + s[i+1:] for s in res])
    return res


def letterCasePermutation(self, S):
    def backtrack(sub="", i=0):
        if len(sub) == len(S):
            res.append(sub)
        else:
            if S[i].isalpha():
                backtrack(sub + S[i].swapcase(), i + 1)
            backtrack(sub + S[i], i + 1)
            
    res = []
    backtrack()
    return res



def letterCasePermutation(self, S):
    S = list(S)
    solutions = ['']
    while S:
        last = S.pop()
        if last.isalpha():
            solutions = [last.lower() + x for x in solutions] + [last.upper() + x for x in solutions]
        else:
            solutions = [last + x for x in solutions]
    return solutions









# official
def letterCasePermutation(self, S):
    ans = [[]]
    for char in S:
        n = len(ans)
        if char.isalpha():
            for i in xrange(n):
                ans.append(ans[i][:])
                ans[i].append(char.lower())
                ans[n+i].append(char.upper())
        else:
            for i in xrange(n):
                ans[i].append(char)

    return map("".join, ans)



def letterCasePermutation(self, S: str) -> List[str]:
    ans=[[]]
    for i in S:
        if i.isdigit():
            for j in ans:
                j.append(i)
        else:
            temp=copy.deepcopy(ans)
            for j in ans:
                j.append(i.lower())
            for k in temp:
                k.append(i.upper())
            ans+=temp
    return [''.join(i) for i in ans]




def letterCasePermutation(self, S: str) -> List[str]:
    if not S:
        return []
    res = ['']
    for i in S:
        temp = []
        for j in res:
            if i in string.ascii_letters:
                temp.append(j + i.upper())
                temp.append(j + i.lower())
            else:
                temp.append(j + i)
        res = temp
    return res


def letterCasePermutation(self, S):
    ans = ['']
    for x in S:
        if x.isdigit():
            ans = [tmp + x for tmp in ans] 
        if x.isalpha():
            tmp1 = [tmp + x.lower() for tmp in ans] 
            tmp2 = [tmp + x.upper() for tmp in ans]
            ans = tmp1 + tmp2
    return ans







def letterCasePermutation(self, S: str) -> List[str]:
	ans=[]
    def helper(s,pre):
        if not s:
            ans.append("".join(pre))
            return
        if s[0].isalpha():
            helper(s[1:],pre+[s[0].upper()])
            helper(s[1:],pre+[s[0].lower()])
        else:
             helper(s[1:],pre+[s[0]])
    helper(S,[])
    print(ans)
    return ans






def letterCasePermutation(self, S: str) -> list:
    ans = []
    def backtrack(S, p):
        ans.append(S)
        for k in range(p, len(S)):
            if 'a' <= S[k] <= 'z':
                backtrack(S[:k]+S[k].upper()+S[k+1:], k+1)
            elif 'A' <= S[k] <= 'Z':
                backtrack(S[:k]+S[k].lower()+S[k+1:], k+1)
        return
    backtrack(S, 0)
    return ans





def letterCasePermutation(self, S):
    B = sum(letter.isalpha() for letter in S)
    ans = []

    for bits in xrange(1 << B):
        b = 0
        word = []
        for letter in S:
            if letter.isalpha():
                if (bits >> b) & 1:
                    word.append(letter.lower())
                else:
                    word.append(letter.upper())

                b += 1
            else:
                word.append(letter)

        ans.append("".join(word))
    return ans






























