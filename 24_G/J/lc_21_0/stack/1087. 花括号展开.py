# 1087. 花括号展开

def expand(self, s: str) -> List[str]:
    res = []
    cur = ""
    for c in s:
        if c == "{":
            res = [r + cur for r in res] if res else [cur]
            cur = ""
        elif  c == "}":
            res = [r + i for r in res for i in cur] if res else [i for i in cur]
            cur = ""
        elif c == ",":
            continue
        else:
            cur += c
    
    if cur:
        if res:
            res = [r + i for r in res for i in cur]
        else:
            res = [cur]
        
    return sorted(res)


        
def expand(self, S: str) -> List[str]:
    res=['']
    n=len(S)
    i=0
    while i<n:
        cur=[]
        if S[i]=='{':
            j=i
            while S[j]!='}':
                j+=1
            cur=S[i+1:j].split(',')
            i=j+1
        else:
            j=i
            while j<n and S[j]!='{':
                j+=1
            cur=[S[i:j]]
            i=j
        res=[i+j for i in res for j in cur]
    return sorted(res)



def expand(self, S: str) -> List[str]:
    ans = [""]
    stack = []
    tag = False
    for s in S:
        if s == ',':
            continue
        if s != "{" and s != "}" and not tag:
           temp = []
           for i in range(len(ans)):
               temp.append(ans[i] + s)
           ans = temp
        elif s != '{' and s != '}':
            stack.append(s)
        elif s == '{':
            tag = True
        elif s == '}':
            tag = False
            temp = []
            for i in range(len(ans)):
                for j in range(len(stack)):
                    temp.append(ans[i] + stack[j])
            ans = temp
            stack.clear()
    ans.sort()
    return ans









































