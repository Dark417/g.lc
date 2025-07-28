# 1441. 用栈操作构建数组

def buildArray(self, target: List[int], n: int) -> List[str]:
    res = []
    j = 0
    for i in range(1, n + 1):
        if i != target[j]:
            res.append("Push")
            res.append("Pop")
            
        else:
            res.append("Push")
            j += 1
        if j == len(target):
            break
    return res













