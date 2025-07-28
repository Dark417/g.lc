# 682. 棒球比赛


def calPoints(self, ops: List[str]) -> int:
    stack = []
    for op in ops:
        if op == '+':
            stack.append(stack[-1] + stack[-2])
        elif op == 'C':
            stack.pop()
        elif op == 'D':
            stack.append(2 * stack[-1])
        else:
            stack.append(int(op))

    return sum(stack)



def calPoints(self, ops: List[str]) -> int:
    l = []
    for c in ops:
        if c == "C" and len(l) > 0:
            l.pop()
        elif c == "D" and len(l) > 0:
            l.append(l[-1]*2)
        elif c == "+" and len(l) > 1:
            l.append(l[-1] + l[-2])
        else:
            l.append(int(c))
    return sum(l)