# 面试题 16.11. 跳水板

def divingBoard(self, shorter: int, longer: int, k: int) -> List[int]:
    if not k:
        return []
    if shorter == longer:
        return [shorter * k]
    res = [0] * (k + 1)
    for i in range(k + 1):
        res[i] = shorter * (k - i) + longer * i
    return res







def divingBoard(self, shorter: int, longer: int, k: int) -> List[int]:
    def dfs(k, cur):
        if k == 0 and cur not in self.s:
            self.s[cur] = 1
        if k != 0:
            for x in (shorter, longer):
                dfs(k-1, cur + x)
    if k == 0:
        return []
    self.s = {}
    dfs(k, 0)
    return sorted(list(self.s.keys()))



















