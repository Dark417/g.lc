"""
211.1055. Shortest Way to Form String
形成字符串的最短路径


对于任何字符串，我们可以通过删除其中一些字符（也可能不删除）来构造该字符串的子序列。

给定源字符串 source 和目标字符串 target，找出源字符串中能通过串联形成目标字符串的子序列的最小数量。如果无法通过串联源字符串中的子序列来构造目标字符串，则返回 -1。

 

示例 1：

输入：source = "abc", target = "abcbc"
输出：2
解释：目标字符串 "abcbc" 可以由 "abc" 和 "bc" 形成，它们都是源字符串 "abc" 的子序列。
示例 2：

输入：source = "abc", target = "acdbc"
输出：-1
解释：由于目标字符串中包含字符 "d"，所以无法由源字符串的子序列构建目标字符串。
示例 3：

输入：source = "xyz", target = "xzyxz"
输出：3
解释：目标字符串可以按如下方式构建： "xz" + "y" + "xz"。
 

提示：

source 和 target 两个字符串都只包含 "a"-"z" 的英文小写字母。
source 和 target 两个字符串的长度介于 1 和 1000 之间。

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/shortest-way-to-form-string
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。




"""


# two pointer greedy O(MN)
class Solution:
    def shortestWay(self, source: str, target: str) -> int:
        num = 0
        t_p = 0
        while t_p < len(target):
            s_p = 0
            flag = False
            while s_p < len(source) and t_p < len(target):
                if source[s_p] == target[t_p]:
                    s_p += 1
                    t_p +=1
                    flag = True
                else:
                    s_p +=1
                    
            if flag == True:
                num +=1
            else:
                return -1
        return num 


# binary search O(NlogM)  
from collections import defaultdict
class Solution:
    
    def shortestWay(self, source: str, target: str) -> int:
        dic = defaultdict(list)
        for ind, char in enumerate(source):
            dic[char].append(ind)
        
        ind = 0
        ans = 1
        for char in target:
            if char not in dic:
                return -1
            else:
                ind, ans= self.binarysearch(source, char, ind, dic, ans)
                
        return ans
                    
    def binarysearch(self, source, char, ind, dic, ans):
        lis = dic[char]
        
        if lis[-1] < ind:
            ans += 1
            ind = 0
            
        l = 0
        r = len(lis)-1
        while l < r:
            mid = (l+r)//2
            if lis[mid] < ind:
                l = mid +1
            else:
                r = mid
    
        return lis[l]+1, ans


# O(N + M) char to index
class Solution:
    def shortestWay(self, source: str, target: str) -> int:
        source_set = set(source)
        
        lis = [[-1]*len(source) for _ in range(26)]
        for ind, char in enumerate(source):
            lis[ord(char)- ord('a')][ind] = ind
        
        for l in lis:
            pre = -1
            for i in range(len(l)-1,-1,-1):
                if l[i] != -1:
                    pre = l[i]
                else:
                    l[i] = pre
        ans = 1
        ind = 0
        for char in target:
            if char not in source_set:
                return -1
            if ind >= len(source):
                ind = 0
                ans += 1
            ind = lis[ord(char) - ord('a')][ind]
            if ind == -1:
                ind = lis[ord(char) - ord('a')][0]  
                ans += 1
            ind +=1

        return ans


# O(N + M)index to char
class Solution:
    def shortestWay(self, source: str, target: str) -> int:
        source_set = set(source)
        
        lis = [[-1]*26 for _ in range(len(source))]
        for i in range(len(lis)-1, -1, -1):
            if i == len(lis)-1:
                lis[i][ord(source[i]) - ord('a')] = i
            else:
                lis[i][:] = lis[i+1]
                lis[i][ord(source[i])-ord('a')] = i 
        
        ans = 1
        ind = 0
        for char in target:
            if char not in source_set:
                return -1
            if ind >= len(lis):
                ind = 0 
                ans +=1
                
            ind = lis[ind][ord(char)-ord('a')]
            if ind == -1:
                ans +=1
                ind = 0
                ind = lis[ind][ord(char)-ord('a')]
            
            ind +=1
            
        return ans






n = len(source)
masks = [1 << j for j in range(n)]
for i in range(2**n):
    yield ''.join([source[j] for j in range(n) if (masks[j] & i)])








def shortestWay(self, source, target):
    s = source * len(target)
    r, cur = len(s)-1, len(target)-1 
    while cur >= 0 and r >= 0:
        if s[r] == target[cur]:
            cur = cur - 1
        r = r - 1
    if cur >= 0:
        return -1
    return len(target) - (r+1)//len(source)







import bisect
from collections import defaultdict
class Solution:
    def shortestWay(self, source: str, target: str) -> int:
        # 哈希表存储字符位置
        hash_set = defaultdict(list)

        for i,c in enumerate(source):
            hash_set[c].append(i)

        cnt, cur = 1, 0

        for c in target:
            # 没有找到key, 返回-1
            if c not in hash_set:
                return -1
            # 如果当前位置大于该字符的最大位置, 那么说明无法继续匹配, 计数器+1, 指针位置是cur=hash_set[c][0] + 1
            if cur > hash_set[c][-1]:
                cnt += 1
                cur = hash_set[c][0] + 1
            # 用二分法寻找最优的位置,当前指针的位置为cur=hash_set[c][pos] + 1
            else:
                pos = bisect.bisect_left(hash_set[c], cur)
                cur = hash_set[c][pos] + 1

        return cnt









































































