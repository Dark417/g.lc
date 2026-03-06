# 20. 有效的括号

def isValid(self, s: str) -> bool:
    if len(s) % 2 == 1:
        return False
    
    pairs = {
        ")": "(",
        "]": "[",
        "}": "{",
    }
    stack = list()
    for ch in s:
        if ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        else:
            stack.append(ch)
    
    return not stack




def isValid(self, s: str) -> bool:
    if len(s) % 2 == 1:
        return False

    stack = []
    for i in s:
        if i in "([{":
            stack.append(i)
        else:
            if i not in ")]}" or len(stack) == 0:
                return False
            else:
                if i == ")" and stack[-1] == "(":
                    stack.pop()
                elif i == "]" and stack[-1] == "[":
                    stack.pop()
                elif i == "}" and stack[-1] == "{":
                    stack.pop()
                else:
                    return False
    return len(stack) == 0



def isValid(self, s: str) -> bool:
    dic = {'{': '}',  '[': ']', '(': ')', '?': '?'}
    stack = ['?']
    for c in s:
        if c in dic: stack.append(c)
        elif dic[stack.pop()] != c: return False 
    return len(stack) == 1



def isValid(self, s: str) -> bool:
    # 入栈与出栈
    stack = []
    for c in s:
        # compare with top element
        if stack and ((stack[-1] + c) in ['()', '{}', '[]']):
            stack.pop()
            continue
        stack.append(c)
    return len(stack) == 0













