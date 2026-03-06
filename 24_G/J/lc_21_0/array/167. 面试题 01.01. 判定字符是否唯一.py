"""
167. 面试题 01.01. 判定字符是否唯一


实现一个算法，确定一个字符串 s 的所有字符是否全都不同。

示例 1：

输入: s = "leetcode"
输出: false 
示例 2：

输入: s = "abc"
输出: true
限制：

0 <= len(s) <= 100
如果你不使用额外的数据结构，会很加分。

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/is-unique-lcci
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

"""

def isUnique(self, astr: str) -> bool:
    #from collections import Counter
    return len(astr) == len(Counter(astr).keys())

	return len(astr) == len(set(astr))


# https://leetcode-cn.com/problems/is-unique-lcci/solution/wei-yun-suan-fang-fa-si-lu-jie-shao-by-zhen-zhu-ha/
# bit
def isUnique(self, astr: str) -> bool:
    mark = 0
    for char in astr:
      move_bit = ord(char) - ord('a')
      if (mark & (1 << move_bit)) != 0:
        return False
      else:
        mark |= (1 << move_bit)
    return True







def isUnique(self, astr: str) -> bool:
    return len({*astr}) == len(astr)

def isUnique(self, astr: str) -> bool:
    s = sorted(astr)
    return all(s[i] != c for i, c in enumerate(s[1: ]))

def isUnique(self, astr: str) -> bool:
        t = 0
        for c in astr:
            if t & (p := 1 << (ord(c) - 97)):
                return False
            t |= p
        return True
























































































