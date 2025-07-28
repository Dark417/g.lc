# 45. 跳跃游戏 II

def jump(self, nums: List[int]) -> int:
	n = len(nums)
	pos = n-1
	steps = 0
	while pos > 0:
		for i in range(pos):
			if i + nums[i] >= pos:
				pos = i
				steps += 1
				break
	return steps


def jump(self, nums: List[int]) -> int:
    n = len(nums)
    maxPos, end, step = 0, 0, 0
    for i in range(n - 1):
        if maxPos >= i:
            maxPos = max(maxPos, i + nums[i])
            if i == end:
                end = maxPos
                step += 1
    return step



























