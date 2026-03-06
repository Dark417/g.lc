# 292. Nim 游戏

# https://leetcode-cn.com/problems/nim-game/solution/ji-yi-hua-di-gui-dong-tai-gui-hua-guan-cha-gui-lu-/

# memo
def canWinNim(self, n: int) -> bool:
	def dfs(n, memo):
		if n <= 3:
			return True
		if memo[n] is not None:
			return memo[n]
		if not dfs(n - 1, memo) or not dfs(n - 2, memo) or not dfs(n - 3, memo)
			memo[n] = True;
			return True

	memo = [None] * (n + 1)
	return dfs(n, memo)



# dp
def canWinNim(self, n: int) -> bool:
	if n <= 3:
		return True
	dp = [0] * (n + 1)
	dp[1] = True
	dp[2] = True
	dp[3] = True
	for i in range(4, n + 1):
		dp[i] = not dp[i - 1] or not dp[i - 2] or not dp[i - 3]
	return dp[n]



# dp arr
def canWinNim(self, n: int) -> bool:
	if n <= 3:
		return True
	dp = [0] * (n + 1)
	dp[1] = True
	dp[2] = True
	dp[3] = True
	for i in range(4, n + 1):
		dp[i] = not dp[i - 1] or not dp[i - 2] or not dp[i - 3]
	return dp[n]






