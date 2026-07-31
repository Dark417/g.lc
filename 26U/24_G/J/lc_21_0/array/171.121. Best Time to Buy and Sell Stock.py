"""
171.121. Best Time to Buy and Sell Stock


Say you have an array for which the ith element is the price of a given stock on day i.

If you were only permitted to complete at most one transaction (i.e., buy one and 
sell one share of the stock), design an algorithm to find the maximum profit.

Note that you cannot sell a stock before you buy one.

Example 1:

Input: [7,1,5,3,6,4]
Output: 5
Explanation: Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.
             Not 7-1 = 6, as selling price needs to be larger than buying price.
Example 2:

Input: [7,6,4,3,1]
Output: 0
Explanation: In this case, no transaction is done, i.e. max profit = 0.
"""


def maxProfit(self, prices: List[int]) -> int:
        minprice = float('inf')
        maxprofit = 0
        for price in prices:
            minprice = min(minprice, price)
            maxprofit = max(maxprofit, price - minprice)
        return maxprofit



def maxProfit(self, prices: List[int]) -> int:
        n = len(prices)
        if n == 0: return 0 # 边界条件
        dp = [0] * n
        minprice = prices[0] 

        for i in range(1, n):
            minprice = min(minprice, prices[i])
            dp[i] = max(dp[i - 1], prices[i] - minprice)

        return dp[-1]



def maxProfit(self, prices: List[int]) -> int:
    if not prices: return 0
    mx, low = 0, prices[0]
    for p in prices:
        mx = max(mx, p - low)
        if p < low:
            low = p
    return mx


def maxProfit(self, prices: List[int]) -> int:
    inf = int(1e9)
    minprice = inf
    maxprofit = 0
    for price in prices:
        maxprofit = max(price - minprice, maxprofit)
        minprice = min(price, minprice)
    return maxprofit



def maxProfit(prices):
	buy, ans = float('inf'), 0
	for p in prices:
		buy, ans = min(buy, p), max(ans, p-buy)
	return ans


# caikehe
# DP
def maxProfit1(self, prices):
    if not prices:
        return 0
    loc = glo = 0
    for i in xrange(1, len(prices)):
        loc = max(loc+prices[i]-prices[i-1], 0)
        glo = max(glo, loc)
    return glo
    
def maxProfit2(self, prices):
    if not prices:
        return 0
    minPri, maxPro = prices[0], 0
    for i in xrange(1, len(prices)):
        minPri = min(minPri, prices[i])
        maxPro = max(maxPro, prices[i]-minPri)
    return maxPro


# Reuse maximum subarray method
def maxProfit(self, prices):
    if not prices or len(prices) == 1:
        return 0
    dp = [0] * len(prices)
    for i in xrange(1, len(prices)):
        dp[i] = prices[i]-prices[i-1]
    glo = loc = dp[0]
    for i in xrange(1, len(dp)):
        loc = max(loc+dp[i], dp[i])
        glo = max(glo, loc)
    return glo


















































