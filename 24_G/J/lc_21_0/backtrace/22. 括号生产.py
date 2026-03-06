"""
077.22. Generate Parentheses
括号生成

Given n pairs of parentheses, write a function to generate all combinations of 
well-formed parentheses.

For example, given n = 3, a solution set is:

[
  "((()))",
  "(()())",
  "(())()",
  "()(())",
  "()()()"
]

"""

# official

 def generateParenthesis(self, n):
    def generate(A = []):
        if len(A) == 2*n:
            if valid(A):
                ans.append("".join(A))
        else:
            A.append('(')
            generate(A)
            A.pop()
            A.append(')')
            generate(A)
            A.pop()

    def valid(A):
        bal = 0
        for c in A:
            if c == '(': bal += 1
            else: bal -= 1
            if bal < 0: return False
        return bal == 0

    ans = []
    generate()
    return ans



def generateParenthesis(self, N):
    ans = []
    def backtrack(S = '', left = 0, right = 0):
        if len(S) == 2 * N:
            ans.append(S)
            return
        if left < N:
            backtrack(S+'(', left+1, right)
        if right < left:
            backtrack(S+')', left, right+1)

    backtrack()
    return ans



def generateParenthesis(self, N):
    if N == 0: return ['']
    ans = []
    for c in xrange(N):
        for left in self.generateParenthesis(c):
            for right in self.generateParenthesis(N-1-c):
                ans.append('({}){}'.format(left, right))
    return ans




# Nick White
def generateParenthesis(self, n: int) -> List[str]:
	def backtrack(res, cur, open, close, max):
		if len(cur) == max*2:
			return cur
		if open < max: backtrack(res, cur+"(", open+1, end+1, max)
		if close < open: backtrack(res, cur+")", open+1, end+1, max)
	res = []
	backtrack(res, "", 0, 0, n)
	return res






def generateParenthesis(self, n: int) -> List[str]:
    ans = []
    def f(l, r, s):
        l == r == n and ans.append(s)
        l < n and f(l + 1, r, s + '(')
        r < l and f(l, r + 1, s + ')')
    f(0, 0, '')
    return ans



def generateParenthesis(self, n: int) -> List[str]:
    if n == 0:
        return [""]
    elif n == 1:
        return ["()"]
    elif n == 2:
        return ["()()", "(())"]
    result = []
    for i in range(n):
        j = n - 1 - i
        temp1 = self.generateParenthesis(i)
        temp2 = self.generateParenthesis(j)
        result.extend(["(%s)%s" % (p, q) for p in temp1 for q in temp2])
    return result



"""
To generate all n-pair parentheses, we can do the following:

Generate one pair: ()

Generate 0 pair inside, n - 1 afterward: () (...)...

Generate 1 pair inside, n - 2 afterward: (()) (...)...

...

Generate n - 1 pair inside, 0 afterward: ((...))

I bet you see the overlapping subproblems here. Here is the code:

(you could see in the code that x represents one j-pair solution and y represents one 
(i - j - 1) pair solution, and we are taking into account all possible of combinations of them)
"""


def generateParenthesis(self, n):
    dp = [[] for i in range(n + 1)]
    dp[0].append('')
    for i in range(n + 1):
        for j in range(i):
            dp[i] += ['(' + x + ')' + y for x in dp[j] for y in dp[i - j - 1]]
    return dp[n]


def generateParenthesis(self, n: int) -> List[str]:
    dp = [set() for i in range(n+1)]
    dp[1] = set(["()"])
    for i in range(2, n+1):
        # include all (n-1) strings by wrapping around with 1 pair of braces
        dp[i].update(["()"+j for j in dp[i-1]])
        dp[i].update([j+"()" for j in dp[i-1]])
        dp[i].update(["("+j+")" for j in dp[i-1]])
  
        # include cases of matching smaller n's for eg, for n=4, we can match n=2 2 times
        for j in range(2, int(n/2)+1):
            for k in dp[i-j]:
                for l in dp[j]:
                    dp[i].add(k+l)
                    dp[i].add(l+k)
    return list(dp[n])




























