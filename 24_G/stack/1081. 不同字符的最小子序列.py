# 1081. 不同字符的最小子序列
# 316. 去除重复字母

def removeDuplicateLetters(self, s) -> int:
    stack = []
    remain_counter = collections.Counter(s)

    for c in s:
        if c not in stack:
            while stack and c < stack[-1] and remain_counter[stack[-1]] > 0:
                stack.pop()
            stack.append(c)
        remain_counter[c] -= 1
    return ''.join(stack)














