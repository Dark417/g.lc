"""
Binary Tree Level Order Traversal I
055.107. Binary Tree Level Order Traversal II

二叉树的层次遍历 II


Given a binary tree, return the bottom-up level order traversal of its nodes' values. (ie, from left to right, level by level from leaf to root).

For example:
Given binary tree [3,9,20,null,null,15,7],
    3
   / \
  9  20
    /  \
   15   7
return its bottom-up level order traversal as:
[
  [15,7],
  [9,20],
  [3]
]




"""


	return [[x.val for x in level] for level in q]


def levelOrderBottom(self, root):
    res, queue = [], [root]
    while queue:
        res.append([node.val for node in queue if node])
        queue = [child for node in queue if node for child in (node.left, node.right)]
    return res[-2::-1]



def levelOrderBottom(self, root):
    queue = []                                                  # 结果列表
    cur = [root]                                                # 接下来要循环的当前层节点，存的是节点
    while cur:                                                  # 当前层存在结点时
        cur_l_val = []                                      # 初始化当前层结果列表为空，存的是val
        next_l_nodes = []                                    # 初始化下一层结点列表为空
        for node in cur:                                        # 遍历当前层的每一个结点
            if node:                                            # 如果该结点不为空，则进行记录
                cur_l_val.append(node.val)                  # 将该结点的值加入当前层结果列表的末尾
                next_l_nodes.extend([node.left, node.right]) # 将该结点的左右孩子结点加入到下一层结点列表
        if cur_l_val:                                       # 只要当前层结果列表不为空
            queue.insert(0, cur_l_val)                      # 则把当前层结果列表插入到队列首端
        cur = next_l_nodes                                   # 下一层的结点变成当前层，接着循环
    return queue


def levelOrderBottom(self, root: TreeNode) -> List[List[int]]:
    from collections import deque
    if not root: return []
    queue = deque()
    queue.appendleft(root)
    res = []
    while queue:
        tmp = []
        n = len(queue)
        for _ in range(n):
            node = queue.pop()
            tmp.append(node.val)
            if node.left:
                queue.appendleft(node.left)
            if node.right:
                queue.appendleft(node.right)
        res.insert(0, tmp)
    return res


def levelOrderBottom(self, root):
    levels = []
    if not root:
        return levels
    cur_layer = [root,]#deque([root,])
    next_layer = []
    while cur_layer:
        levels.insert(0,[])#levels.append([])
        for node in cur_layer:
            levels[0].append(node.val) #this change from levels[-1].append(node.val)
            if node.left:
                next_layer.append(node.left)
            if node.right:
                next_layer.append(node.right)
        cur_layer = next_layer
        next_layer = []
    return levels


# lol
def levelOrderBottom(self, root: TreeNode) -> List[List[int]]:
        res=[]
        level=0
        flag=0
        stack=[(root,flag,level)]
        while stack:
            node,flag,level=stack.pop()
            if node is None: continue
            if flag==0:
                stack.append((node.right,0,level+1))
                stack.append((node.left,0,level+1))
                stack.append((node,1,level))
            else:
                if(len(res)==level): res.insert(0,[]) # insert实现头部插入list
                res[-1-level].append(node.val) # -1-level 实现尾部添加元素
        return res


def levelOrderBottom(self, root: TreeNode) -> List[List[int]]:
    if not root:
        return []
    ans = [root]
    target = []
    while ans:
        tmp,n = [],len(ans)
        for i in range(n):
            r = ans.pop(0)
            tmp.append(r.val)
            if r.left:
                ans.append(r.left)
            if r.right:
                ans.append(r.right)
        target.append(tmp)
    return target[::-1]



# recursion
def levelOrderBottom(self, root: TreeNode) -> List[List[int]]:
        res = []
        def helper(root, depth):
            if not root: return 
            if depth == len(res):
                res.insert(0, [])
            res[-(depth+1)].append(root.val)
            helper(root.left, depth+1)
            helper(root.right, depth+1)
        helper(root, 0)
        return res


def levelOrderBottom(self, root: TreeNode) -> List[List[int]]:
        if not root:
            return []
        ans = [root]
        target = []
        
        def subfunc(ans):
            tmp = []
            n = len(ans)
            for i in range(n):
                r = ans.pop(0)
                tmp.append(r.val)
                if r.left:
                    ans.append(r.left)
                if r.right:
                    ans.append(r.right)
            target.append(tmp)
            if ans == []:
                pass
            else:
                subfunc(ans)
        subfunc(ans)
        return target[::-1]



# dfs
def levelOrderBottom(self, root: TreeNode) -> List[List[int]]:
    if not root:
        return []
    res = {}

    def dfs(r, n):
        if n in res:
            res[n].append(r.val)
        else:
            res[n] = [r.val]
        if r.left:
            dfs(r.left, n + 1)
        if r.right:
            dfs(r.right, n + 1)

    dfs(root, 1)
    	result = [res[k] for k in sorted(res.keys(),key=lambda x:x, reverse=True)]
    return result


def levelOrderBottom(self, root):
    if root is None:return []
    else:
        maxDepth=self.maxDepth(root)
        resultList=[]
        for i in range(maxDepth):
            resultList.append([])
        resultList[maxDepth-1].append(root.val)
        self.solr(maxDepth-2,root.left,root.right,resultList)
        return resultList
        #开始遍历
def solr(self,depth,left,right,resultList):
    if left is not None:
        resultList[depth].append(left.val)
        self.solr(depth-1,left.left,left.right,resultList)
    if right is not None:
        resultList[depth].append(right.val)
        self.solr(depth-1,right.left,right.right,resultList)
def maxDepth(self, root):
    if root is None: return 0
    else: return max(self.maxDepth(root.left),self.maxDepth(root.right))+1


def levelOrder(self, root):
        result = []
        self.helper(root, 0, result)
        return result
    
    def helper(self, root, level, result):
        if root is None:
            return
        if len(result) <= level:
            result.append([])
        result[level].append(root.val)
        self.helper(root.left, level+1, result)
        self.helper(root.right, level+1, result)


# bfs
def levelOrderBottom(self, root: TreeNode) -> List[List[int]]:
    if root==None:
        return []
    if root.left==None and root.right==None:
        return [[root.val]]
    ans=[]
    search=[root]
    n=1
    while n!=0:
        ans.insert(0,[])
        while n!=0:
            n-=1
            a=search.pop(0)
            ans[0].append(a.val)
            if a.left!=None:
                search.append(a.left)
            if a.right!=None:
                search.append(a.right)
        n=len(search)
    return ans


def levelOrderBottom(self, root: TreeNode) -> List[List[int]]:
    if root == None:
        return []
    stack = [root]
    result = []
    while len(stack) != 0:
        num = len(stack)
        r_temp = []
        for i in range(num):
            node = stack.pop(0)
            r_temp.append(node.val)
            if node.left:
                stack.append(node.left)
            if node.right:
                stack.append(node.right)
        result.insert(0, r_temp)
    return result


def levelOrderBottom(self, root):
    answ, L = [], [root]
    while L and root:
        answ.insert(0,[n.val for n in L])
        L = [ C for N in L for C in (N.left,N.right) if C ]
    return answ


def levelOrderBottom(self, root):
    res, nodes = [], [root] if root else []
    while nodes:
        res.append(list(node.val for node in nodes))
        nodes = [x for node in nodes for x in (node.left, node.right) if x]
    res.reverse()
    return res


def levelOrderBottom(self, root):
	res,data=[],[]
    if not root:return res
    stack=[]
    stack.append(root)
    nCount=1#记录每层节点数
    while stack:
        node=stack.pop(0)
        data+=[node.val]#保存每层节点的值
        nCount-=1
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
        if nCount==0:
            res=[data]+res
            data=[]
            nCount=len(stack)
    return res

def levelOrder(self, root):
    q, result = deque(), []
    if root:
        q.append(root)
    while len(q):
        level = []
        for _ in range(len(q)):
            x = q.popleft()
            level.append(x.val)
            if x.left:
                q.append(x.left)
            if x.right:
                q.append(x.right)
        result.append(level)
    return result


# 6
def levelOrder(self, root):
    ans, level = [], [root]
    while root and level:
        ans.append([node.val for node in level])
        LRpair = [(node.left, node.right) for node in level]
        level = [leaf for LR in LRpair for leaf in LR if leaf]
    return ans


def levelOrder(self, root):
    ans, level = [], [root]
    while root and level:
        ans.append([node.val for node in level])            
        level = [kid for n in level for kid in (n.left, n.right) if kid]
    return ans


def levelOrder(self, root):
    if not root:
        return []
    ans, level = [], [root]
    while level:
        ans.append([node.val for node in level])
        temp = []
        for node in level:
            temp.extend([node.left, node.right])
        level = [leaf for leaf in temp if leaf]
    return ans


# deep depth

##  use queue to implement BFS, needs to record level
class Solution:
    def levelOrderBottom(self, root: TreeNode) -> List[List[int]]:
        queue = collections.deque()
        queue.append((root,0))
        res = []
        if not root:
            return res
        while queue:
            node,depth = queue.popleft()
            if node:
                if len(res) <= depth:
                    res.insert(0,[])
                
                res[-(depth+1)].insert(0,node.val)
                queue.insert(0,(node.left,depth+1))
                queue.insert(0,(node.right,depth+1))
            
        return res
## use stack to implement DFS, record depth
class Solution:
    def levelOrderBottom(self, root: TreeNode) -> List[List[int]]:
        res = []
        stack = [(root, 0)]
        while len(stack) > 0:
            node, depth = stack.pop()
            if node:
                if len(res) <= depth:
                    res.insert(0, [])
                res[-(depth+1)].append(node.val)
                stack.append((node.right, depth+1))
                stack.append((node.left, depth+1))
        return res
        
## Recursive DFS
class Solution:
    def levelOrderBottom(self, root: TreeNode) -> List[List[int]]:
        res = []
        self.dfs(root, 0, res)
        return res

    def dfs(self, root, depth, res):
        if root:
            if depth >= len(res):
                res.insert(0, [])
            res[-(depth+1)].append(root.val)
            self.dfs(root.left, depth+1, res)
            self.dfs(root.right, depth+1, res)



def levelOrderBottom(self, root):
    queue, res = collections.deque([(root, 0)]), []
    while queue:
        node, level = queue.popleft()
        if node:
            if level == len(res):
                res.append([])
            res[level].append(node.val)
            queue.append((node.left, level + 1))
            queue.append((node.right, level + 1))
    return res[::-1]


# dfs recursively
def levelOrderBottom1(self, root):
    res = []
    self.dfs(root, 0, res)
    return res

def dfs(self, root, level, res):
    if root:
        if len(res) < level + 1:
            res.insert(0, [])
        res[-(level+1)].append(root.val)
        self.dfs(root.left, level+1, res)
        self.dfs(root.right, level+1, res)
        
# dfs + stack
def levelOrderBottom2(self, root):
    stack = [(root, 0)]
    res = []
    while stack:
        node, level = stack.pop()
        if node:
            if len(res) < level+1:
                res.insert(0, [])
            res[-(level+1)].append(node.val)
            stack.append((node.right, level+1))
            stack.append((node.left, level+1))
    return res
 
# bfs + queue   
def levelOrderBottom(self, root):
    queue, res = collections.deque([(root, 0)]), []
    while queue:
        node, level = queue.popleft()
        if node:
            if len(res) < level+1:
                res.insert(0, [])
            res[-(level+1)].append(node.val)
            queue.append((node.left, level+1))
            queue.append((node.right, level+1))
    return res






















































