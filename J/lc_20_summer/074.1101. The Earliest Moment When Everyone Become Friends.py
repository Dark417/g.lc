"""
074.1101. The Earliest Moment When Everyone Become Friends
彼此熟识的最早时间


在一个社交圈子当中，有 N 个人。每个人都有一个从 0 到 N-1 唯一的 id 编号。

我们有一份日志列表 logs，其中每条记录都包含一个非负整数的时间戳，以及分属两个人的不同 id，logs[i] = [timestamp, id_A, id_B]。

每条日志标识出两个人成为好友的时间，友谊是相互的：如果 A 和 B 是好友，那么 B 和 A 也是好友。

如果 A 是 B 的好友，或者 A 是 B 的好友的好友，那么就可以认为 A 也与 B 熟识。

返回圈子里所有人之间都熟识的最早时间。如果找不到最早时间，就返回 -1 。

 

示例：

输入：logs = [[20190101,0,1],[20190104,3,4],[20190107,2,3],[20190211,1,5],[20190224,2,4],[20190301,0,3],[20190312,1,2],[20190322,4,5]], N = 6
输出：20190301
解释：
第一次结交发生在 timestamp = 20190101，0 和 1 成为好友，社交朋友圈如下 [0,1], [2], [3], [4], [5]。
第二次结交发生在 timestamp = 20190104，3 和 4 成为好友，社交朋友圈如下 [0,1], [2], [3,4], [5].
第三次结交发生在 timestamp = 20190107，2 和 3 成为好友，社交朋友圈如下 [0,1], [2,3,4], [5].
第四次结交发生在 timestamp = 20190211，1 和 5 成为好友，社交朋友圈如下 [0,1,5], [2,3,4].
第五次结交发生在 timestamp = 20190224，2 和 4 已经是好友了。
第六次结交发生在 timestamp = 20190301，0 和 3 成为好友，大家都互相熟识了。
 

提示：

1 <= N <= 100
1 <= logs.length <= 10^4
0 <= logs[i][0] <= 10^9
0 <= logs[i][1], logs[i][2] <= N - 1
保证 logs[i][0] 中的所有时间戳都不同
Logs 不一定按某一标准排序
logs[i][1] != logs[i][2]

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/the-earliest-moment-when-everyone-become-friends
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

"""

class UF:
    def __init__(self, N):
        # 初始化
        self.amount = [1] * N
        self.parent = [i for i in range(N)]

    def find(self, x):
        while x != self.parent[x]:
            x = self.parent[x]
        return x


    def union(self, p, q):
        # 先找到p,q的最父亲节点
        proot = self.find(p)
        qroot = self.find(q)
        if proot == qroot:
            return

        # 这里其实谁做谁父亲，都可以
        self.parent[proot] = qroot

        # 但是一定确认谁是父亲以后，子的朋友圈人数就得加到父亲的朋友圈人数里去
        self.amount[qroot] += self.amount[proot]

class Solution(object):
    def earliestAcq(self, logs, N):
        """
        :type logs: List[List[int]]
        :type N: int
        :rtype: int
        """
        # part = {}
        # def root(u):
        #     if not par[u]: return u
        #     par[u] = root(par[u])

        # S = {{i} for i in range(N)}
        # par[u] = par[root(v)]
    
        uf = UF(N)

        # 因为logs第一个元素是时间，所以我们先对时间进行一个排序
        # 因为朋友圈的形成是按照时间点的顺序来发生的
        logs.sort()

        for time, a, b in logs:

            # 每次让a,b所属的朋友圈结交一下
            uf.union(a, b)

            # 这里find(a) 或是(b)都没关系，因为他们已经成为一个朋友圈
            # 所以这两个点向上找都肯定会找到同一个root
            # 并且这个root已经被我们处理过， a,b两个朋友圈的人数早已复制到amount[root]里去了
            if uf.amount[uf.find(a)] == N:
                return time

        return -1




# 2
class MergeSet:
    def __init__(self, init_list):
        self.m = {i:i for i in init_list}

    def getRoot(self, node):
        root = node
        buf = []
        while self.m[root] != root:
            buf.append(root)
            root = self.m[root]
        for node in buf:
            self.m[node] = root

        return root


    def merge(self, a, b):
        for node in [a, b]:
            if node not in self.m:
                self.m[node] = node

        root1 = self.getRoot(a)
        root2 = self.getRoot(b)
        if root1 != root2:
            self.m[root1] = root2

    def isInSameSet(self, a, b):
        for node in [a, b]:
            if node not in self.m:
                return False

        return self.getRoot(a) == self.getRoot(b)

    def getRootNum(self):
        cnt = 0
        for key in self.m.keys():
            if self.m[key] == key:
                cnt += 1
        return cnt


from typing import List
class Solution:
    def earliestAcq(self, logs: List[List[int]], N: int) -> int:
        merge_set = MergeSet(range(N))
        logs.sort(key = lambda x : x[0])




























