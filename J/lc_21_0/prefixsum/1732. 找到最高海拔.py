# 1732. 找到最高海拔

def largestAltitude(self, gain: List[int]) -> int:
    n = len(gain)
    presum = [0] * (n+1)
    for i in range(n):
        presum[i+1] = presum[i] + gain[i]
    return max(presum)