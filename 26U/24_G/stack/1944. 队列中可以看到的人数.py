1944. 队列中可以看到的人数

def canSeePersonsCount(self, heights: List[int]) -> List[int]:
    n = len(heights)
    res = [0] * n
    stack = []
    cur = 0

    for i in range(n - 1, -1, -1):
        while stack and heights[i] > stack[-1]:
            cur += 1
            stack.pop()
        if stack:
            cur += 1
        res[i] = cur

        cur = 0
        stack.append(heights[i])

    return res



def canSeePersonsCount(self, heights: List[int]) -> List[int]:
    n = len(heights)
    stack = []
    res = [0] * n
    for i in range(n - 1, -1, -1):
        h = heights[i]
        while stack and h > stack[-1]:
            res[i] += 1
            stack.pop()
        if stack:
            res[i] += 1
        stack.append(h)
    return res













