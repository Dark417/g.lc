# 306. 累加数

def isAdditiveNumber(self, num: str) -> bool:
    if len(num) < 3:
        return False
    self.res = False
    def backTrack(rest, tmp_cnt, last1, last2):
        if tmp_cnt <= 2 and not rest:
            return
        if not rest:
            self.res = True
            return

        for i in range(len(rest)):
            if len(rest[:i+1]) != len(str(int(rest[:i+1]))):
                return
            if tmp_cnt >=2:     # 当tmp_cnt>=2时即已经分出两个数时才需要判断
                if int(rest[:i+1]) == last1 + last2:    # 剪枝--
                    backTrack(rest[i + 1:], tmp_cnt + 1, last2, int(rest[:i + 1]))
            else:
                backTrack(rest[i + 1:], tmp_cnt + 1, last2, int(rest[:i + 1]))
            if self.res:    
                return
    backTrack(num,0,0,0)
    return self.res


def isAdditiveNumber(self, num: str) -> bool:
    def dfs(start, a, b, picked_cnt):
        if start == len(num) and picked_cnt > 2: return True # 找到了
        for i in range(start, len(num)):
            if num[start] == '0' and i != start: return False # 不能以 0 开头，除非是 0 本身
            if picked_cnt < 2 and dfs(i + 1, b, int(num[start:i+1] or '0'), picked_cnt + 1): return True
            if int(num[start:i+1] or '0') == a + b and dfs(i + 1, b, int(num[start:i+1] or '0'), picked_cnt + 1): return True
        return False
    if len(num) < 3: return False
    return dfs(0, 0, 0, 0)




# to be debugged // bug ded...
def isAdditiveNumber(self, num: str) -> bool:
    def dfs(start, cnt, a, b):
        if cnt <= 2 and start == len(num):
            return
        if start == len(num):
            self.res = True
            return
        
        for i in range(start, len(num)):
            if num[start] == "0" and i > start:
                return
            if cnt >= 2:
                if int(num[start: i + 1]) == a + b:
                    dfs(i + 1, cnt + 1, b, int(num[start: i + 1]))
            else:
                dfs(i + 1, cnt + 1, b, int(num[start: i + 1]))
        if self.res:
            return

    if len(num) < 3:
        return False
    self.res = False
    dfs(0, 0, 0, 0)
    return self.res




def isAdditiveNumber(self, num: str) -> bool:
    if len(num) < 3: return False
    res = False
    def dfs(begin, path, left_num):
        nonlocal res
        if len(path) > 2 and left_num == 0: 
            res = True
            return
        for i in range(begin + 1, len(num) + 1):
            if i > begin + 1 and num[begin] == '0': return
            if len(path) < 2:
                dfs(i, path + [int(num[begin:i])], len(num) - i)
            else:
                if int(num[begin:i]) == path[-1] + path[-2]:
                    dfs(i, path + [int(num[begin: i])], len(num) - i)
    
    dfs(0, [], len(num))
    return  res





def isAdditiveNumber(self, num: str) -> bool:
    def check(s1,s2,tar):
        if (s1[0]=='0' and len(s1)!=1) or (s2[0]=='0' and len(s2)!=1):
            return False
        if len(tar)==0:return True
        tmp = str(int(s1)+int(s2))
        if tar.find(tmp)!=0:
            return False
        else:
            return check(s2,tmp,tar[len(tmp):])

    n = len(num)
    for i in range(1,n-1):
        for j in range(i+1,n):
            if check(num[:i],num[i:j],num[j:]):
                return True
    return False



def isAdditiveNumber(self, num: str) -> bool:
    if len(num) < 3:
        return False

    def backtrack(n1, n2, r):
        s = str(int(n1) + int(n2))
        if s == r:
            return True
        elif len(s) > len(r) or r[:len(s)] != s:
            return False
        else:
            return backtrack(n2, s, r[len(s):])
            
    def is_invalid_num(n):
    	return len(n) > 1 and n[0] == '0'

    for i in range(1, len(num) + 1):                            # 找到第一个数：num[:i]
        for j in range(i + 1, len(num)):                        # 找到第二个数：num[i:j]
            num1, num2, rest = num[:i], num[i:j], num[j:]
            if is_invalid_num(num1) or is_invalid_num(num2):    # 避免0开头的非0数
                continue
            if backtrack(num1, num2, rest):
                return True
    return False


def isAdditiveNumber(self, num: str) -> bool:
    Start=[]
    for i in range(1,len(num)-1):
        for j in range(i+1,len(num)):
            sum_s=str(int(num[:i])+int(num[i:j]))
            l=len(sum_s)
            if num[j:j+l]==sum_s:
                Start.append([int(num[:i]),int(num[i:j])])

    for ans in Start:
        length=len(str(ans[0]))+len(str(ans[1]))
        while length<len(num):
            ans.append(ans[-1]+ans[-2])
            length+=len(str(ans[-1]))
        if ''.join(map(str,ans))==num:
            return True
    return False


def isAdditiveNumber(self, num):
    n = len(num)
    for i, j in itertools.combinations(range(1, n), 2):
        a, b = num[:i], num[i:j]
        if b != str(int(b)):
            continue
        while j < n:
            c = str(int(a) + int(b))
            if not num.startswith(c, j):
                break
            j += len(c)
            a, b = b, c
        if j == n:
            return True
    return False
