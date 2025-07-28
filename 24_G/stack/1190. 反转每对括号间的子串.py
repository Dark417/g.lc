# 1190. 反转每对括号间的子串

def reverseParentheses(s: str) -> str:
    stack = []
    for c in s:
        if c != ")":
            stack.append(c)
        elif c == ")":
            tmp = []
            while stack and stack[-1] != "(":
                tmp.append(stack.pop())
            stack.pop()
            stack += tmp
    return "".join(stack)


def reverseParentheses(self, s: str) -> str:
    stk = []
    word = ""
    for c in s:
        if c == '(':        #遇到新的一段了
            stk.append(word)    #这段进stk
            word = ""           #新的一段开始统计
        elif c == ')':
            word = stk.pop() + word[::-1] #这一段要翻转了，与前面的一段可以接起来
        else:
            word += c           #统计入当前的这一段
    return word



def reverseParentheses(self, s: str) -> str:
    stack = []
    n = len(s)
    pair = [0] * n

    # 预先存储左右括号的映射关系
    for i in range(n):
        if s[i] == '(':
            stack.append(i)
        if s[i] == ')':
            j = stack.pop()
            pair[i] = j
            pair[j] = i 
    
    index = 0
    # step = 1 表示向右走, step = -1 表示向左走
    step = 1
    result = []
    while index < n:
        if s[index] == '(' or s[index] == ')':
            index = pair[index]
            # 走的方向反转
            step = -step
        else:
            result.append(s[index])
        index += step
    return "".join(result)






























