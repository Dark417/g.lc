# 1893. 检查是否区域内所有整数都被覆盖

def isCovered(self, ranges: List[List[int]], left: int, right: int) -> bool:
    n = len(ranges)
    diff = [0] * 52
    for rang in ranges:
        diff[rang[0]] += 1
        diff[rang[1] + 1] -= 1
    presum = [0] * 52
    for i in range(51):
        presum[i + 1] = presum[i] + diff[i+1] 

    for i in range(left, right + 1):
        if presum[i] <= 0:
            return False
    return True

def isCovered(self, ranges: List[List[int]], left: int, right: int) -> bool:
    diff = [0] * 52   # 差分数组
    for l, r in ranges:
        diff[l] += 1
        diff[r+1] -= 1
    # 前缀和
    curr = 0
    for i in range(1, 51):
        curr += diff[i]
        if left <= i <= right and curr <= 0:
            return False
    return True


def isCovered(self, ranges: List[List[int]], left: int, right: int) -> bool:
    dc = set()
    for rang in ranges:
        for n in range(rang[0], rang[1]+1):
            if n not in dc:
                dc.add(n)
    return all(i in dc for i in range(left, right+1))



















