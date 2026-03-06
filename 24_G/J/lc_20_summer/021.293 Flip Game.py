"""
021.293	Flip Game
翻转游戏

你和朋友玩一个叫做「翻转游戏」的游戏，游戏规则：给定一个只有 + 和 - 的字符串。你和朋友轮流将 连续 的两个 "++" 反转成 "--"。 当一方无法进行有效的翻转时便意味着游戏结束，则另一方获胜。

请你写出一个函数，来计算出第一次翻转后，字符串所有的可能状态。

 

示例：

输入: s = "++++"
输出: 
[
  "--++",
  "+--+",
  "++--"
]
注意：如果不存在可能的有效操作，请返回一个空列表 []。



"""

def generatePossibleNextMoves(self, s):
    ret = []
    if len(s) == 1: return ret
    if len(s) == 2:
        if s == "++": 
            ret.append("--")
    else:
        for i in range(len(s)-1):
            if s[i:i+2] == "++":
                ret.append(s[:i] + "--" + s[i+2:])
    
    return ret


def generatePossibleNextMoves(self, s):
    ans,n = [],len(s)
    if n<2:
        return ans
    i,j = 0,1
    while i<j and j<n:
        tmp = s
        if tmp[i]=="+" and tmp[j]=="+":
            ans.append(tmp[:i]+"--"+tmp[j+1:])
        i+=1
        j+=1
    return ans


def generatePossibleNextMoves(self, s: str) -> List[str]:
    return {s[0:i]+s[i:].replace('++','--',1) for i in range(len(s)-1) if '++' in s[i:]}











