# 1262. 可被三整除的最大和

def maxSumDivThree(self, nums: List[int]) -> int:
    dp = [0, 0, 0]

    for a in nums:
        for i in dp[:]:
            dp[(i + a) % 3] = max(dp[(i + a) % 3], i + a)
    return dp[0]



def maxSumDivThree(self, nums: List[int]) -> int:
    mod_1, mod_2,res,remove = [], [], 0, float('inf')
    for i in nums:
        if i%3 == 0: res += i
        if i%3 == 1: mod_1 += [i]
        if i %3 == 2: mod_2 += [i]
    mod_1.sort(reverse = True)
    mod_2.sort(reverse = True)
    tmp = sum(mod_1) +sum(mod_2)
    if tmp % 3 == 0:
        return res + tmp
    elif tmp% 3 == 1:
        if len(mod_1): remove = min(remove,mod_1[-1])
        if len(mod_2) > 1: remove = min(mod_2[-1]+mod_2[-2],remove)
    elif tmp % 3 == 2:
        if len(mod_2): remove = min(remove,mod_2[-1])
        if len(mod_1) > 1: remove = min(mod_1[-1]+mod_1[-2],remove)
    return res + tmp - remove



def maxSumDivThree(self, nums: List[int]) -> int:
	n = len(nums)
	dp = [[0]*3 for _ in range(n+1)]
	dp[0][1] = float('-inf')
	dp[0][2] = float('-inf')
	for i in range(1, n+1):
		if nums[i-1] % 3 == 0: # Current remainder == 0
			dp[i][0] = max(dp[i-1][0], dp[i-1][0] + nums[i-1]) # Current remainder is 0, so we add to dp[i-1][0] to keep the remainder 0
			dp[i][1] = max(dp[i-1][1], dp[i-1][1] + nums[i-1]) # Current remainder is 0, so we add to dp[i-1][1] to keep the remainder 1
			dp[i][2] = max(dp[i-1][2], dp[i-1][2] + nums[i-1]) # Current remainder is 0, so we add to dp[i-1][2] to keep the remainder 2
		elif nums[i-1] % 3 == 1: # Current remainder == 1
			dp[i][0] = max(dp[i-1][0], dp[i-1][2] + nums[i-1]) # Current remainder is 1, so we add to dp[i-1][2] to keep the remainder 0
			dp[i][1] = max(dp[i-1][1], dp[i-1][0] + nums[i-1]) # Current remainder is 1, so we add to dp[i-1][0] to keep the remainder 1
			dp[i][2] = max(dp[i-1][2], dp[i-1][1] + nums[i-1]) # Current remainder is 1, so we add to dp[i-1][1] to keep the remainder 2
		else: # Current remainder == 2
			dp[i][0] = max(dp[i-1][0], dp[i-1][1] + nums[i-1]) # Can you tell how this works now?
			dp[i][1] = max(dp[i-1][1], dp[i-1][2] + nums[i-1])
			dp[i][2] = max(dp[i-1][2], dp[i-1][0] + nums[i-1])

	return dp[-1][0]



def maxSumDivThree(self, nums: List[int]) -> int:
    f = [[0] * 3 for i in range(len(nums))]
    f[0][nums[0] % 3] = nums[0]
    for i in range(1, len(nums)):
        for j in range(3):
            include = f[i-1][(j + 3 - nums[i] %3) % 3] + nums[i]
            if include % 3 == j:
                f[i][j] = max(f[i-1][j], include)
            else:
                f[i][j] = f[i-1][j]
    return f[-1][0]





















