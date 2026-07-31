# 2073. 买票需要的时间

def timeRequiredToBuy(self, tickets: List[int], k: int) -> int:
    n = len(tickets)
    res = 0
    for i in range(n):
        # 遍历计算每个人所需时间
        if i <= k:
            res += min(tickets[i], tickets[k])
        else:
            res += min(tickets[i], tickets[k] - 1)
    return res



def timeRequiredToBuy(self, tickets: List[int], k: int) -> int:
    res, idx, n = 0, 0, len(tickets)
    while tickets[k]:
        if tickets[idx % n]:
            tickets[idx % n] -= 1
            res += 1
        idx += 1
    return res



