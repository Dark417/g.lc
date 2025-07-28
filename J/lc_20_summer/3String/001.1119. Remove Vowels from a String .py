"""
001.1119. Remove Vowels from a String

给你一个字符串 S，请你删去其中的所有元音字母（ 'a'，'e'，'i'，'o'，'u'），并返回这个新字符串。

 

示例 1：

输入："leetcodeisacommunityforcoders"
输出："ltcdscmmntyfrcdrs"
示例 2：

输入："aeiou"
输出：""
 

提示：

S 仅由小写英文字母组成。
1 <= S.length <= 1000

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/remove-vowels-from-a-string
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

"""

"""
"".join([i for i in S if i not in l])
"".join(i for i in S if i not in 'aeiou')
"".join([i for i in S if i not in ['a', 'e', 'i', 'o', 'u']])
S.replace('a', '').replace('e', '').replace('i', '').replace('o', '').replace('u', '')

"""

import re
def removeVowels(self, S: str) -> str:
    return re.sub('[aeiou]','',S)


def removeVowels(self, S: str) -> str:
    l = ['a', 'e', 'i', 'o', 'u']
    i = 0

    def removechar(ss, i):
        if i == len(l):
            return ss
        return removechar(ss.replace(l[i], ''), i + 1)

    return removechar(S, i)


def removeVowels(self, S: str) -> str:
    l = ['a', 'e', 'i', 'o', 'u']
    return "".join([i for i in S if i not in l])
    return ''.join(i for i in S if i not in 'aeiou')
    return ''.join([i for i in S if i not in ['a', 'e', 'i', 'o', 'u']])
    return S.replace('a', '').replace('e', '').replace('i', '').replace('o', '').replace('u', '')


def removeVowels(self, S: str) -> str:
    result = ''
    for x in S:
        if not x in ['a', 'e', 'i', 'o', 'u']:
            result += x
    return result

    r = []
    for s in S:
        if s not in {'a', 'e', 'i', 'o', 'u'}:
            r.append(s)
    return ''.join(r)





