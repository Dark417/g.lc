"""
034.面试题 10.02. 变位词组


编写一种方法，对字符串数组进行排序，将所有变位词组合在一起。变位词是指字母相同，
但排列不同的字符串。

注意：本题相对原题稍作修改

示例:

输入: ["eat", "tea", "tan", "ate", "nat", "bat"],
输出:
[
  ["ate","eat","tea"],
  ["nat","tan"],
  ["bat"]
]
说明：

所有输入均为小写字母。
不考虑答案输出的顺序

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/group-anagrams-lcci
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。




"""

def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
    dic = {}
    ret = []
    for i in range(len(strs)):
        if ''.join(sorted(strs[i])) not in dic:
            dic[''.join(sorted(strs[i]))] = [strs[i]]
        else:
            dic[''.join(sorted(strs[i]))].append(strs[i])
    for val in dic.values():
        ret.append(val)
    return ret


























