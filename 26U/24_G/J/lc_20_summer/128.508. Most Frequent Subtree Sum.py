"""
128.508. Most Frequent Subtree Sum


Given the root of a tree, you are asked to find the most frequent subtree sum. 
The subtree sum of a node is defined as the sum of all the node values formed 
by the subtree rooted at that node (including the node itself). So what is the 
most frequent subtree sum value? If there is a tie, return all the values with 
the highest frequency in any order.

Examples 1
Input:

  5
 /  \
2   -3
return [2, -3, 4], since all the values happen only once, return all of them in any order.
Examples 2
Input:

  5
 /  \
2   -5
return [2], since 2 happens twice, however -5 only occur once.
Note: You may assume the sum of values in any subtree is in the range of 32-bit signed integer.

"""

def findFrequentTreeSum(self, root: TreeNode) -> List[int]:
    if not root: return 
    res = []
    def dfs(node):
        if not node: return 0
        x = node.val + dfs(node.left) + dfs(node.right)
        res.append(x)
        return x
    dfs(root)
    res.sort()
    from collections import Counter
    c = Counter(res)
    maxCount = max(c.values())
    return [s for s in c if c[s] == maxCount]



def findFrequentTreeSum(self, root):
    if root is None: return []

    def dfs(node):
        if node is None: return 0
        s = node.val + dfs(node.left) + dfs(node.right)
        count[s] += 1
        return s

    count = collections.Counter()
    dfs(root)
    maxCount = max(count.values())
    return [s for s in count if count[s] == maxCount]






def findFrequentTreeSum(self, root):
def helper(root, d):
    if not root:
        return 0
    left = helper(root.left, d)
    right = helper(root.right, d)
    subtreeSum = left + right + root.val
    d[subtreeSum] = d.get(subtreeSum, 0) + 1
    return subtreeSum
    
    d = {}
    helper(root, d)
    mostFreq = 0
    ans = []
    for key in d:
        if d[key] > mostFreq:
            mostFreq = d[key]
            ans = [key]
        elif d[key] == mostFreq:
            ans.append(key)
    return ans



def findFrequentTreeSum(self, root: TreeNode) -> List[int]:
    if not root: return []
    D = collections.defaultdict(int)
    # DFS recursively
	def cal_sum(node):
        if not node: return 0
        rv = node.val + cal_sum(node.left) + cal_sum(node.right)
        D[rv] += 1
        return rv
    cal_sum(root)
    mx = max(D.values())
    return [k for k, v in D.items() if v == mx] # return key if its val == max



def findFrequentTreeSum(self, root: TreeNode) -> List[int]:
    def treeSum(root):
        s = root.val
        if root.left:
            s += treeSum(root.left)
        if root.right:
            s += treeSum(root.right)
        subtree_sums[s] = subtree_sums.get(s, 0) + 1
        return s
    
    if not root:
        return []
    subtree_sums = {}
    treeSum(root)
    f_max = max(subtree_sums.values())
    return [s for s in subtree_sums if subtree_sums[s] == f_max]


def findFrequentTreeSum(self, root):
    if not root:
        return []
    self.sums = collections.defaultdict(int)
    self.dfs(root)
    res = []
    max_freq = max(self.sums.values())
    for stree_sum in self.sums:
        if self.sums[stree_sum] == max_freq:
            res.append(stree_sum)
    return res
    
def dfs(self, node):
    if node:
        left = self.dfs(node.left)
        right = self.dfs(node.right)
        self.sums[right + left + node.val] += 1
        return right + left + node.val
    return 0


def findFrequentTreeSum(self, root):
    if not root:
        return []
    a=defaultdict(int)
    def helper(root):
        b=root.val
        if root.left:
            b+=helper(root.left)
        if root.right:
            b+=helper(root.right)
        a[b]+=1
        return b
    helper(root)
    m=max(a.values())
    return [k for k in a if a[k]==m]


def findFrequentTreeSum(self, root: TreeNode) -> List[int]:
    
    sumFreqCount = defaultdict(int)
    maxFreq = 0
    
    def subTreeSum(root: TreeNode)->int:
        nonlocal sumFreqCount
        nonlocal maxFreq
        if not root:
        res = subTreeSum(root.left) + root.val + subTreeSum(root.right)
        sumFreqCount[res] += 1
        if sumFreqCount[res] > maxFreq:
            maxFreq = sumFreqCount[res]        
        return res
    subTreeSum(root)
    return [ key for key,freq in sumFreqCount.items() if freq == maxFreq]



def findFrequentTreeSum(self, root):
    if root is None: return []
    h = collections.defaultdict(int)
    self.f(root,h)
    freq = max(h.values())
    return [key for key in h if h[key] == freq]
def f(self,node,h):
    if node is None: return 0
    v = node.val + self.f(node.left,h) + self.f(node.right,h)
    h[v] +=1
    return v



def findFrequentTreeSum(self, root):
    dic = defaultdict(lambda: 0)
    self.helper(root, dic)
    mostFreqSubSum = []
    times = 0
    for s, t in dic.items():
        if t > times:
            mostFreqSubSum = [s]
            times = t
        elif t == times:
            mostFreqSubSum.append(s)
    return mostFreqSubSum

def helper(self, node, dic):
    if not node:
        return 0
    subsum = self.helper(node.left, dic) + self.helper(node.right, dic) + node.val
    dic[subsum] += 1
    return subsum












































