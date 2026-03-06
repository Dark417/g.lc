# 1598. 文件夹操作日志搜集器

def minOperations(self, logs: List[str]) -> int:
    stack = []
    for log in logs:
        if log == "../":
            if stack:
                stack.pop()
            else:
                continue
        elif log != "./":
            stack.append(log)
    return len(stack)


def minOperations(self, logs: List[str]) -> int:
    ans = 0 
    for log in logs:
        if log.startswith("../"):
            ans -= 1
        elif log.startswith("./"):
            ans += 0
        else:
            ans += 1
        ans = ans if ans > 0 else 0
    return ans


























