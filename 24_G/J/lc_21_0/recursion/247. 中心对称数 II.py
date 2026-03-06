# 246. 中心对称数
def isStrobogrammatic(self, num: str) -> bool:
    if len(num) == 1:
        if num in ("1", "0", "8"):
            return True
        else:
            return False
    if len(num) > 1 and num[0] == "0":
        return False
    n = len(num)
    if n%2 != 0 and num[n//2] not in ("0", "1", "8"):
        return False
    dc = {"1":"1", "8":"8", "6":"9", "9":"6", "0":"0"}
    
    for i in range(len(num)//2):
        if num[i] not in dc:
            return False
        if num[-i-1] == dc[num[i]]:
            continue
        else:
            return False
    return True


def isStrobogrammatic(self, num: str) -> bool:
    if len(num) == 1:
        if num in ("1", "0", "8"):
            return True
        else:
            return False
    if len(num) > 1 and num[0] == "0":
        return False
    n = len(num)
    if n%2 != 0 and num[n//2] not in ("0", "1", "8"):
        return False
    dc = {"1":"1", "8":"8", "6":"9", "9":"6", "0":"0"}
    i, j = 0, n - 1
    while i <= j:
        if num[i] not in dc or num[j] not in dc:
            return False
        if num[j] != dc[num[i]]:
            return False
        i += 1
        j -= 1
    return True
        
def isStrobogrammatic(self, num: str) -> bool:
    ans = ''
    for i in num:
        if i == '2' or i == '3' or i == '4' or i == '5' or i == '7':
            return False
        elif i == '9':  # 遇到6或者9需要换一下
            a = '6'
            ans += a
        elif i == '6':
            a = '9'
            ans += a
        else:
            a = i
            ans += a
        print(ans)
    if num != ans[::-1]:
        return False
    return True



"""
bool isStrobogrammatic(string num) {
    if (num.empty()) {
        return false; // no number
    }
    unordered_map<char, char> mp = {{'1', '1'}, {'6', '9'}, {'8', '8'}, {'9', '6'}, {'0', '0'}};
    int N = num.size();
    for (int i = 0, j = N - 1; i <= j; i++, j--) {
        // Note: always check exist or not before use it, although it also works
        // with check exist or not in this case, but undefined behavior may occur
        // better be conservative
        if (!mp.count(num[i]) || (mp[num[i]] != num[j])) {
            return false;
        }
    }

    return true;
}


"""








# 247. 中心对称数 II

def findStrobogrammatic(self, n: int) -> List[str]:
    def helper(left, right, tmp = [None] * n, res = tuple()):
        if left > right: return ("".join(tmp),)
        for k, v in (('0', '0'), ('1', '1'), ('6', '9'), ('8', '8'), ('9', '6')):
            if not left and right and k == '0' or left == right and k != v: continue
            tmp[left], tmp[right] = k, v
            res += helper(left + 1, right - 1)
        return res
    return helper(0, n - 1)



def findStrobogrammatic(self, n: int) -> List[str]:
    dict = {"1":"1", "6":"9", "9":"6", "8":"8"}
    def fun(x):
        if x == 0:
            return [""]
        elif x == 1:
            return ["0", "1", "8"]
        ans = []
        for num in fun(x - 2):
            for key, value in dict.items():
                ans.append(key + num + value)
                
            if x != n:
                ans.append("0" + num + "0")
        return ans
    return fun(n)


def findStrobogrammatic(self, n: int) -> List[str]:
    def getSymm(s):
        res= ""
        for c in s[::-1]:
            if c=="6" or c=="9":
                res += str(15-int(c))
            else:
                res += c
        return res
    def dfs(s,num,l):
        if len(s)==num:
            l.append(s)
            return 
        tem = ["0","1","8","6","9"]
        if len(s)==0:
            tem.remove("0")
        for c in tem:
            tem_s = s+c
            dfs(tem_s,num,l)
    num = n//2
    l = []
    dfs("",num,l)
    if n%2==0:
        l = [s+getSymm(s) for s in l]
    else:
        l =[s+c+getSymm(s) for s in l for c in ["0","1","8"]]
    return l   



# 248. 中心对称数 III


















