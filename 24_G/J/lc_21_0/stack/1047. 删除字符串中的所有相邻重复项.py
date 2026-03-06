# 1047. 删除字符串中的所有相邻重复项

def removeDuplicates(self, S: str) -> str:
    i, j, n = 0, 0, len(S)
    res = list(S)
    while j < n:
        res[i] = res[j]
        if i > 0 and res[i - 1] == res[i]:
            i -= 2
        i += 1
        j += 1
    return "".join(res[:i])


# 2pt
def removeDuplicates(self, S: str) -> str:
    end, a = -1, list(S)
    for c in a:
        if end >= 0 and a[end] == c:
            end -= 1
        else:
            end += 1
            a[end] = c
    return ''.join(a[: end + 1])


# 
def removeDuplicates(self, S: str, k: int) -> str:
    stk = []
    for char in S:
        if not stk or stk[-1][0] != char:
            stk.append([char, 1])
        elif stk[-1][1] + 1 < k:
            stk[-1][1] += 1
        else:
            stk.pop()
    return ''.join(char * cnt for char, cnt in stk)


# recursive
def removeDuplicates(self, S: str) -> str:
    i = 1
    while i < len(S):
        if S[i-1] == S[i]:
            return self.removeDuplicates(S[0: i-1] + S[i+1:])
        i += 1
    return S



def removeDuplicates(self, S):
    return reduce(lambda s, c: s[:-1] if s[-1:] == c else s + c, S)


def removeDuplicates(self, S: str) -> str:
    stk = list()
    for ch in S:
        if stk and stk[-1] == ch:
            stk.pop()
        else:
            stk.append(ch)
    return "".join(stk)


def removeDuplicates(self, S: str) -> str:
    stack = []
    i = 0
    while i < len(S):
        c = S[i]
        if stack:
            if c == stack[-1]:
                stack.pop()
            else:
                stack.append(c)
        else:
            stack.append(c)
        i += 1
    return "".join(stack)





















