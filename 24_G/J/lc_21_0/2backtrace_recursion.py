# recursion


# 面试题 08.06. 汉诺塔问题

def hanota(self, A: List[int], B: List[int], C: List[int]) -> None:
    n = len(A)
    self.move(n, A, B, C)
# 定义move 函数移动汉诺塔
def move(self,n, A, B, C):
    if n == 1:
        C.append(A[-1])
        A.pop()
        return 
    else:
        self.move(n-1, A, C, B)  # 将A上面n-1个通过C移到B
        C.append(A[-1])          # 将A最后一个移到C
        A.pop()                  # 这时，A空了
        self.move(n-1,B, A, C)   # 将B上面n-1个通过空的A移到C



# 095.17. Letter Combinations of a Phone Number 电话号码的字母组合
def letterCombinations(self, digits: str) -> List[str]:
    dc = {"1":"!@#", "2":"abc", "3":"def", "4":"ghi", "5":"jkl", "6":"mno", "7":"pqrs", "8":"tuv","9":"wxyz",}
    res = []
    for d in digits:
        if res == []:
            res = [i for i in dc[d]]
        else:
            res = [ x+i for x in res for i in dc[d]]
    return res


# 097.39. Combination Sum 组合总和
def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
    def dfs(candidates, begin, size, path, res, target):
        if target == 0:
            res.append(path)
            return

        for index in range(begin, size):
            residue = target - candidates[index]
            if residue < 0:
                break

            dfs(candidates, index, size, path + [candidates[index]], res, residue)

    size = len(candidates)
    if size == 0:
        return []
    candidates.sort()
    path = []
    res = []
    dfs(candidates, 0, size, path, res, target)
    return res


# 544. 输出比赛匹配对
def findContestMatch(self, n: int) -> str:
    tm = list(map(str, range(1, n+1)))
    while n > 1:
        for i in range(int(n//2)):
            tm[i] = "(" + tm[i] + "," + tm.pop() + ")"
        n /= 2
    return tm[0]

# map not subscriptable
# n/2 is float
# 4/2 = 2.0
# range(4/2) is float
# range(4//2) ok but not in this quesiton???









































































