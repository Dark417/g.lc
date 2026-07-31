"""
070.199. Binary Tree Right Side View 
二叉树的右视图
Given a binary tree, imagine yourself standing on the right side of it, 
return the values of the nodes you can see ordered from top to bottom.

Example:

Input: [1,2,3,null,5,null,4]
Output: [1, 3, 4]
Explanation:

   1            <---
 /   \
2     3         <---
 \     \
  5     4       <---



while (!Q.empty())
{
    size = Q.size()
    for i in range 0..size
    {
        node = Q.pop()
        Q.push(node.left)
        Q.push(node.right)
    }
}



"""



def rightSideView(self, root: TreeNode) -> List[int]:
	if not root: return []
    res = []
    cur = [root]
    while cur:
        lnext = []
        res.append(cur[-1].val)
        while cur:
            node = cur.pop(0)
            if node.left:
                lnext.append(node.left)
            if node.right:
                lnext.append(node.right)
        cur = lnext
    return res


def rightSideView(self, root: TreeNode) -> List[int]:
    if not root: return []
    res = []
    cur = [root]
    while cur:
        lnext = []
        res.append(cur[0].val)
        while cur:
            node = cur.pop(0)
            if node.right:
                lnext.append(node.right)
            if node.left:
                lnext.append(node.left)
        cur = lnext
    return res



# Stefan
# recursive combined right left
def rightSideView(self, root):
    if not root:
        return []
    right = self.rightSideView(root.right)
    left = self.rightSideView(root.left)
    return [root.val] + right + left[len(right):]


    def rightSideView(self, root):
        if root==None:
            return []
        ans=[root.val]
        left=ans+self.rightSideView(root.left)
        right=ans+self.rightSideView(root.right)
        if len(right)>=len(left):
            return right
        return right+left[len(right):]


# dfs, first come first serve
def rightSideView(self, root):
    def collect(node, depth):
        if node:
            if depth == len(view):
                view.append(node.val)
            collect(node.right, depth+1)
            collect(node.left, depth+1)
    view = []
    collect(root, 0)
    return view


# bfs, iterative
def rightSideView(self, root):
    view = []
    if root:
        level = [root]
        while level:
            view += level[-1].val
            level = [kid for node in level for kid in (node.left, node.right) if kid]
    return view


    ans,level=[],[root]
    while root and level:
        ans.append(level[-1].val)
        level=[k for n in level for k in (n.left,n.right) if k]
    return ans

    queue = [root] if root else []


# caikehe
# DFS recursively
def rightSideView(self, root):
    res = []
    self.dfs(root, 0, res)
    return [x[0] for x in res]
    
def dfs(self, root, level, res):
    if root:
        if len(res) < level+1:
            res.append([])
        res[level].append(root.val)
        self.dfs(root.right, level+1, res)
        self.dfs(root.left, level+1, res)


def rightSideView1(self, root):
    res = []
    self.dfs(root, 0, res)
    return res
    
def dfs(self, root, level, res):
    if root:
        if len(res) == level:
            res.append(root.val)
        self.dfs(root.right, level+1, res)
        self.dfs(root.left, level+1, res)


# DFS + stack
def rightSideView2(self, root):
    res, stack = [], [(root, 0)]
    while stack:
        curr, level = stack.pop()
        if curr:
            if len(res) < level+1:
                res.append([])
            res[level].append(curr.val)
            stack.append((curr.right, level+1))
            stack.append((curr.left, level+1))
    return [x[-1] for x in res]

# DFS + stack
def rightSideView2(self, root):
    res, stack = [], [(root, 0)]
    while stack:
        curr, level = stack.pop()
        if curr:
            if len(res) == level:
                res.append(curr.val)
            stack.append((curr.left, level+1))
            stack.append((curr.right, level+1))
    return res


# BFS + queue
def rightSideView(self, root):
    res, queue = [], [(root, 0)]
    while queue:
        curr, level = queue.pop(0)
        if curr:
            if len(res) < level+1:
                res.append([])
            res[level].append(curr.val)
            queue.append((curr.left, level+1))
            queue.append((curr.right, level+1))
    return [x[-1] for x in res]
        
# BFS + queue
def rightSideView3(self, root):
    res, queue = [], [(root, 0)]
    while queue:
        curr, level = queue.pop(0)
        if curr:
            if len(res) == level:
                res.append(curr.val)
            queue.append((curr.right, level+1))
            queue.append((curr.left, level+1))
    return res





def rightSideView(self, root):
    res, nxtL= [], [root] if root else []
    while nxtL:
        res.append(nxtL[-1].val) # right most val as to output
        curL, nxtL = nxtL, []
        for i in curL: # build the next level
            if i.left: nxtL.append(i.left)
            if i.right: nxtL.append(i.right)
    return res



# panda model
def rightSideView(self, root: TreeNode) -> List[int]:
        if not root:
            return []
        res = []
        tmp_layer = collections.deque()  # 还是BFS用到的queue
        tmp_layer.append(root)  # 先将初始节点压入
        while len(tmp_layer) > 0:
            count = 0  # 计数，用来记录是某一层的第几个元素
            next_layer = []
            while len(tmp_layer) > 0:  # 处理某一层的节点
                tmp_node = tmp_layer.popleft()
                if count == 0:  # 根据题意只要最右侧的元素，所以根据下面先压入队列的是右子树，后压入左子树，我们只要队列中的第一个元素
                    res.append(tmp_node.val)
                count += 1
                # 将某个节点的右左子树压入
                if tmp_node.right is not None:
                    next_layer.append(tmp_node.right)
                if tmp_node.left is not None:
                    next_layer.append(tmp_node.left)
            tmp_layer = collections.deque(next_layer)  # 更新下一层的tmp
        return res



# official
# bfs
def rightSideView(self, root):
    rightmost_value_at_depth = dict() # 深度为索引，存放节点的值
    max_depth = -1

    queue = deque([(root, 0)])
    while queue:
        node, depth = queue.popleft()

        if node is not None:
            # 维护二叉树的最大深度
            max_depth = max(max_depth, depth)

            # 由于每一层最后一个访问到的节点才是我们要的答案，因此不断更新对应深度的信息即可
            rightmost_value_at_depth[depth] = node.val

            queue.append((node.left, depth+1))
            queue.append((node.right, depth+1))

    return [rightmost_value_at_depth[depth] for depth in range(max_depth+1)]


# dfs
def rightSideView(self, root: TreeNode) -> List[int]:
	rightmost_value_at_depth = dict() # 深度为索引，存放节点的值
    max_depth = -1

    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()

        if node is not None:
            # 维护二叉树的最大深度
            max_depth = max(max_depth, depth)

            # 如果不存在对应深度的节点我们才插入
            rightmost_value_at_depth.setdefault(depth, node.val)

            stack.append((node.left, depth+1))
            stack.append((node.right, depth+1))

    return [rightmost_value_at_depth[depth] for depth in range(max_depth+1)


#dp
def rightSideView(self, root: TreeNode) -> List[int]:
        if not root:
            return []
        tmp = [root]
        ret = [[root.val]]
        while tmp:
            a = tmp[:]
            tmp = []
            ret += [[]]
            for i in a:
                if i.left:
                    tmp += [i.left]
                    ret[-1] += [i.left.val]
                if i.right:
                    tmp += [i.right]
                    ret[-1] += [i.right.val]
        return [i[-1] for i in ret[:-1]]





# bfs
def rightSideView(self, root: TreeNode) -> List[int]:
    import collections
    if not root: return []
    
    res = []
    queue = collections.deque([(root, 1)])  # (node, depth)
    layer = 0
    while queue:
        top = queue.popleft()
        if top[1] != layer:  # this layer's first node
            res.append(top[0].val)
            layer += 1  # go next layer
        if top[0].right:  # right child first in
            queue.append((top[0].right, top[1]+1))
        if top[0].left:
            queue.append((top[0].left, top[1]+1))
    return res



def rightSideView(self, root: TreeNode) -> List[int]:
    if not root:
        return []
    ret = []
    stack = [(root, 1)]
    while stack:
        node, level = stack.pop()
        if level > len(ret):
            ret.append(node.val)
        if node.left:
            stack.append((node.left, level+1))
        if node.right:
            stack.append((node.right, level+1))
    return ret


def rightSideView(self, root: TreeNode) -> List[int]:
    res = []
    if not root:
        return res
    q = Queue()
    q.put(root)
    while q.qsize() > 0:
        q_size = q.qsize()
        i = 0
        while i < q_size:
            node = q.get()
            if i == q_size - 1:
                res.append(node.val)
            if node.left:
                q.put(node.left)
            if node.right:
                q.put(node.right)
            i = i + 1
    return res


































