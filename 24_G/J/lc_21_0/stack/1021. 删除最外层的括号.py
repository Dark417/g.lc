# 1021. 删除最外层的括号

def removeOuterParentheses(self, S: str) -> str:
    s1 = s2 = 0
    res = []
    for i in S:
        if s1 == 0:
            s1 += 1
        elif s2 == 0:
            if i == "(":
                s2 += 1
                res.append(i)
            else:
                s1 -= 1
        else:
            s2 = s2 + 1 if i == "(" else s2 - 1
            res.append(i)
    return "".join(res)


def removeOuterParentheses(self, s: str) -> str:
    ans=''
    stack=[]
    l,r=0,0
    for i in s:
        stack.append(i)
        if i=='(':
            l+=1
        if i==')':
            r+=1
        if stack and l==r:
            for i in stack[1:-1]:
                ans=ans+str(i)
            stack=[]
    return ans


def removeOuterParentheses(self, S: str) -> str:
    lv = 0
    res = []
    for i in S:
        if i == "(":
            lv += 1
            if lv > 1:
                res.append(i)
        else:
            lv -= 1
            if lv != 0:
                res.append(i)
    return "".join(res)


def removeOuterParentheses(self, S: str) -> str:
    lv = 0
    res = []
    for i in S:
        if i == "(":
            if lv > 0:
                res.append(i)
            lv += 1
        else:
            if lv != 1:
                res.append(i)
            lv -= 1
    return "".join(res)









