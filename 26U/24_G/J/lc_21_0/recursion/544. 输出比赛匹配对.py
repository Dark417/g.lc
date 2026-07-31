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

def findContestMatch(self, n: int) -> str:
    res=list(map(str,range(1,n+1)))
    while(n>1):
        n/=2
        i=0
        while(i<n):
            res[i]="("+res[i]+","+res[-i-1]+")"
            i+=1
        res=res[:i]
    return res[0]



def findContestMatch(self, n):
    team = map(str, range(1, n+1))
    while n > 1:
        for i in xrange(n / 2):
            team[i] = "({},{})".format(team[i], team.pop())
        n /= 2
    return team[0]


def findContestMatch(self, n):
    temp = [[i,str(i)] for i in range(1,n+1) ]

    res =[]
    def match(temp,size):
        if size==1:
            res.append(temp[0][1])
            return 
        curtemp = []
        for i in range(size//2):
            val = max(int(temp[i][0]),int(temp[size-1-i][0]))
            str1 = '('+temp[i][1]+','+temp[size-1-i][1]+')'
            curtemp.append([val,str1])

        curtemp.sort(key=lambda x:int(x[0]),reverse=True)
        match(curtemp,size//2)
    
    match(temp,n)
    return res[0]



def findContestMatch(self, n):
    team = []
    ans = []
    def write(r):
        if r == 0:
            i = len(team)
            w = i & -i
            team.append(n/w+1 - team[i-w] if w else 1)
            ans.append(str(team[-1]))
        else:
            ans.append("(")
            write(r-1)
            ans.append(",")
            write(r-1)
            ans.append(")")

    write(int(math.log(n, 2)))
    return "".join(ans)






































