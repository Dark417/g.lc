"""
208.1025. Divisor Game
除数博弈



"""


def divisorGame(self, N: int) -> bool:
    return N%2==0
    return ~N%2


def divisorGame(self, N: int) -> bool:
    target = [0 for i in range(N+1)]
    target[1] = 0 #若爱丽丝抽到1，则爱丽丝输
    if N<=1:
        return False
    else:
    
        target[2] = 1 #若爱丽丝抽到2，则爱丽丝赢
        for i in range(3,N+1):
            for j in range(1,i//2):
                # 若j是i的余数且target[i-j]为假（0）的话，则代表当前为真（1）
                if i%j==0 and target[i-j]==0:
                    target[i] = 1
                    break
        return target[N]==1


def divisorGame(self, N: int) -> bool:
    dp = [False for i in range(N+1)]
    for i in range(N+1):
         for j in range(1, i//2 + 1):
                if i % j == 0 and (not dp[i - j]):
                    dp[i] = True
                    break
    return dp[N]
















































































