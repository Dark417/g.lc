"""
015.1180 Count Substrings with Only One Distinct Letter

给你一个字符串 S，返回只含 单一字母 的子串个数。

示例 1：

输入： "aaaba"
输出： 8
解释： 
只含单一字母的子串分别是 "aaa"， "aa"， "a"， "b"。
"aaa" 出现 1 次。
"aa" 出现 2 次。
"a" 出现 4 次。
"b" 出现 1 次。
所以答案是 1 + 2 + 4 + 1 = 8。
示例 2:

输入： "aaaaaaaaaa"
输出： 55
 

提示：

1 <= S.length <= 1000
S[i] 仅由小写英文字母组成。


"""


def countLetters(self, S):

    def recur(n):
        if n > 0:
            return n + recurn(n-1)
        else:
            return 0

    i = 0
    d = {}
    d2 = {}
    #acc = 1

    while i < len(S):
        print(i)
        if S[i] not in d:
            d[S[i]] = 1
        else:
            if S[i] == S[i-1]:
                d[S[i]] += 1
            else:
                if S[i] not in d2:
                    d2[S[i]] = 1
                else:
                    d2[S[i]] += 1

        i += 1

    num = 0
    for (key, val) in d:
        num += recur(val)
    
    for (key, val) in d2:
        num += val

    return num




























