# 103. 二叉树的锯齿形层序遍历

def zigzagLevelOrder(self, root: TreeNode) -> List[List[int]]:
    if not root: return []
    res = []
    cur_level = [root]
    depth = 0
    while cur_level:
        tmp = []
        next_level = []
        for node in cur_level:
            tmp.append(node.val)
            if node.left:
                next_level.append(node.left)
            if node.right:
                next_level.append(node.right)
        if depth % 2 == 1:
            res.append(tmp[::-1])
        else:
            res.append(tmp)
        depth += 1
        cur_level = next_level
    return res

def zigzagLevelOrder(self, root: TreeNode) -> List[List[int]]:
    if not root:
        return []

    curr = [root]
    res = []
    while curr:
        temp = []
        n = len(curr)
        for i in range(n):
            node = curr.pop(0)
            temp.append(node.val)
            if node.left:
                curr.append(node.left)
            if node.right:
                curr.append(node.right)
        res.append(temp)

    return [res[i][::-1]  if i % 2 == 1 else res[i]  
            for i in range(len(res)) ]



def zigzagLevelOrder(self, root: TreeNode) -> List[List[int]]:
    res = []
    
    def helper(root, depth):
        if not root: return 
        if len(res) == depth:
            res.append([])
        if depth % 2 == 0:res[depth].append(root.val)
        else: res[depth].insert(0, root.val)
        helper(root.left, depth + 1)
        helper(root.right, depth + 1)
    helper(root, 0)
    return res




def zigzagLevelOrder(self, root: TreeNode) -> List[List[int]]:
    stack = [root]
    res = []
    while stack:
        level = []
        for _ in range(len(stack)):
            node = stack.pop(0)
            if not node:
                continue
            level.append(node.val)
            stack.append(node.left)
            stack.append(node.right)
        if level:
            res.append(level)
    for i in range(1,len(res),2):
        res[i] = res[i][::-1]
    return res


def zigzagLevelOrder(self, root: TreeNode) -> List[List[int]]:
    if not root:
        return []

    res = []
    deque_ = deque()
    deque_.append(root)
    is_even_level = True # 奇偶层

    while deque_:

        # 每一层的
        level = deque()
        for i in range(len(deque_)):
            node = deque_.popleft()
            if is_even_level:
                level.append(node.val)
            else:
                level.appendleft(node.val)
            if node.left:
                deque_.append(node.left)
            if node.right:
                deque_.append(node.right)
            
        res.append(list(level)) # 要转成list，否则会报错
        is_even_level = not is_even_level
    
    return res



def zigzagLevelOrder(self, root: TreeNode) -> List[List[int]]:
    if not root:
        return []        
    queue = deque()
    queue.append(root)
    
    is_even_level = True
    ans = []
    while queue:
        level_queue = deque()
        size = len(queue)
        
        for _ in range(size):
            node = queue.popleft()
            if is_even_level:
                level_queue.append(node.val)
            else:
                level_queue.appendleft(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        ans.append(list(level_queue))
        is_even_level = not is_even_level
    
    return ans


















