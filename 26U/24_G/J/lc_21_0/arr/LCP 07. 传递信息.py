# LCP 07. 传递信息


def numWays(self, n: int, relation: List[int], k: int) -> int:
    dp = [[0]*(n) for t in range(0,k+1)]
    dp[0][0] = 1

    for t in range(0,k):
        for x,y in relation:
            dp[t+1][y] += dp[t][x]
    return dp[k][n-1]



def numWays(self, n: int, relation: List[int], k: int) -> int:
    self.n, self.k, self.res = n, k, 0
    self.rel_dict = collections.defaultdict(list)
    for x,y in relation:
        self.rel_dict[x].append(y)

    self.search(0,0)
    return self.res 

def search(self, index, num):
    if num==self.k:
        if index==self.n-1:
            self.res += 1
        return
    for i in self.rel_dict[index]:
        self.search(i, num+1)











