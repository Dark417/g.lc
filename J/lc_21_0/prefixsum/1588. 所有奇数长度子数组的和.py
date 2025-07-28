# 1588. 所有奇数长度子数组的和


def sumOddLengthSubarrays(self, arr: List[int]) -> int:
    sum = 0
    n = len(arr)
    prefixSums = [0] * (n + 1)
    for i, v in enumerate(arr):
        prefixSums[i + 1] = prefixSums[i] + v
    for start in range(n):
        length = 1
        while start + length <= n:
            end = start + length - 1
            sum += prefixSums[end + 1] - prefixSums[start]
            length += 2
    return sum




def sumOddLengthSubarrays(self, arr: List[int]) -> int:
	sm = 0
	n = len(arr)
	leng = 1
	while leng <= n:
		for s in range(n):
			if s + leng <= n:
				for i in range(s, s + leng):
					sm += arr[i]
		leng += 2
	return sm


def sumOddLengthSubarrays(self, arr: List[int]) -> int:
    sum = 0
    n = len(arr)
    for start in range(n):
        length = 1
        while start + length <= n:
            for v in arr[start:start + length]:
                sum += v
            length += 2
    return sum





























