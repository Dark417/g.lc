# 1544. 整理字符串

def makeGood(self, s: str) -> str:
    stack = []
    
    for c in s:
        if not stack:
            stack.append(c)
        else: 
            cur = stack[-1]
            if cur.islower() and cur.upper() == c or cur.isupper() and cur.lower() == c:
                stack.pop()
            else:
                stack.append(c)
    return "".join(stack)



def makeGood(self, s: str) -> str:
    ret = list()
    for ch in s:
        if ret and ret[-1].lower() == ch.lower() and ret[-1] != ch:
            ret.pop()
        else:
            ret.append(ch)
    return "".join(ret)
















