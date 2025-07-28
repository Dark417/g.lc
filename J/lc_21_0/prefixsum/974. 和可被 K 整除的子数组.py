# 974. 和可被 K 整除的子数组


def subarraysDivByK(self, nums: List[int], k: int) -> int:
    record = {0: 1}
    total, ans = 0, 0
    for elem in nums:
        total += elem
        modulus = total % k
        same = record.get(modulus, 0)
        ans += same
        record[modulus] = same + 1
    return ans


def subarraysDivByK(self, nums: List[int], k: int) -> int:
    record = {0: 1}
    total = 0
    for elem in nums:
        total += elem
        modulus = total % k
        record[modulus] = record.get(modulus, 0) + 1
    
    ans = 0
    for x, cx in record.items():
        ans += cx * (cx - 1) // 2
    return ans










