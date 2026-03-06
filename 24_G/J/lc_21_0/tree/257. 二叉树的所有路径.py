# 257. 二叉树的所有路径


def binaryTreePaths(self, root: TreeNode) -> List[str]:
    def dfs(node, cur):
        if not node: return
        now = cur[:]
        now.append(node.val)
        if not node.left and not node.right:
            self.res.append(now)
        dfs(node.left, now)
        dfs(node.right, now)
            
    self.res = []
    dfs(root, [])
    return ["->".join(str(i) for i in r) for r in self.res]
    return ["->".join(map(str, r)) for r in self.res]
    return ["->".join(map(lambda x: str(x), r)) for r in self.res]

def binaryTreePaths(self, root):
    def construct_paths(root, path):
        if root:
            path += str(root.val)
            if not root.left and not root.right:  # 当前节点是叶子节点
                paths.append(path)  # 把路径加入到答案中
            else:
                path += '->'  # 当前节点不是叶子节点，继续递归遍历
                construct_paths(root.left, path)
                construct_paths(root.right, path)

    paths = []
    construct_paths(root, '')
    return paths


def binaryTreePaths(self, root: TreeNode) -> List[str]:
    paths = list()
    if not root:
        return paths

    node_queue = collections.deque([root])
    path_queue = collections.deque([str(root.val)])

    while node_queue:
        node = node_queue.popleft()
        path = path_queue.popleft()

        if not node.left and not node.right:
            paths.append(path)
        else:
            if node.left:
                node_queue.append(node.left)
                path_queue.append(path + '->' + str(node.left.val))
            
            if node.right:
                node_queue.append(node.right)
                path_queue.append(path + '->' + str(node.right.val))
    return paths
