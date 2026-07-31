# 254. 因子的组合

def getFactors(self, n):
    self.res = []
    self.backtrack(n, 2, [])
    return self.res

def backtrack(self, n, index, cur):
    for i in range(index, int(n ** 0.5) + 1):
        if n % i == 0:
            self.res.append(sorted(cur + [n // i, i]))
            self.backtrack(n // i, i, [i] + cur)




def getFactors(self, n: int) -> List[List[int]]:
    self.visited=set()
    def dfs(m:int,path:list):
        left=path[-1] if path else 2
        for i in range(left,int(m**0.5)+1):
            if m%i==0:
                a=tuple(path+[i,m//i])
                if a not in self.visited:
                    self.visited.add(a)
                dfs(m//i,path+[i])
    
    dfs(n,[])
    return [list(i) for i in self.visited]


    
def getFactors(self, n: int) -> List[List[int]]:
    res = []
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            comb = sorted([i, n // i])
            if comb not in res:#去重
                res.append(comb)
            for item in self.getFactors(n // i) :
                comb = sorted([i] + item)
                if comb not in res:#去重
                    res.append(comb)
    return res





def getFactors(self, n: int) -> List[List[int]]:
    res = []
    for i in range(2,int(sqrt(n)+1)):
      if n % i == 0:
        remain = self.getFactors(int(n/i))
        res.append([i,int(n/i)])
        for x in remain:
          if x[0] >= i:
            res.append([i,*x])
    return res









































