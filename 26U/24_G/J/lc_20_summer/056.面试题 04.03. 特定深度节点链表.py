"""
056.面试题 04.03. 特定深度节点链表








"""

# dfs
def listOfDepth(self, root: TreeNode) -> List[ListNode]:
        ans = []
        def dfs(node, level):
            if not node: return None
            if len(ans) == level:
                ans.append(ListNode(node.val))
            else:
                head = ListNode(node.val)
                head.next = ans[level]
                ans[level] = head
            dfs(node.right, level + 1)
            dfs(node.left, level + 1)
        dfs(root, 0)
        return ans





# dfs3
def listOfDepth(self, tree: TreeNode) -> List[ListNode]:
        res = []
        self.list_of_depth_core(tree, res, 1)
        return res

    def list_of_depth_core(self, tree: TreeNode, nodes: List[ListNode], depth: int) -> None:
        """
        携带状态的 深度优先搜索
        :param tree: 待处理节点 
        :param nodes: 每层节点
        :param depth: 当前深度
        """
        if not tree:
            return
        
        # 第一次到达该深度，那么创建对应的头节点
        if len(nodes) < depth:
            node = ListNode(tree.val)
            nodes.insert(depth - 1, node)
        # 之后到达该深度的，就直接在链表尾部接上即可
        else:
            node = nodes[depth - 1]
            while node.next:
                node = node.next
            node.next = ListNode(tree.val)
        
        # 处理下一层
        self.list_of_depth_core(tree.left, nodes, depth + 1)
        self.list_of_depth_core(tree.right, nodes, depth + 1)





# bfs

def listOfDepth(self, tree: TreeNode) -> List[ListNode]:
    from collections import deque
    if tree is None:
        return []
    res = []  # 结果集
    temp = deque()
    temp.append(tree)
    while len(temp) > 0:  # BFS模板开始
        tmp_dummy_node = ListNode(None)  # 创建dummynode
        cur = tmp_dummy_node
        next_layer = []  # 存储下一层元素
        while len(temp) != 0:  # 将某一层中的全部取出处理
            node = temp.popleft()
            cur.next = ListNode(node.val)  # 将一层中的组合成链表
            cur = cur.next
            if node.left is not None:
                next_layer.append(node.left)
            if node.right is not None:
                next_layer.append(node.right)
        res.append(tmp_dummy_node.next)  # 压入结果集
        temp = deque(next_layer.copy())
    return res


def listOfDepth(self, tree: TreeNode) -> List[ListNode]:
        res = []
        if not tree:
            return res
        stack = [tree]
        while stack:
            n = len(stack)
            head = ListNode(None)
            cur = head
            for i in range(n):
                node = stack.pop(0)
                if node.left:
                    stack.append(node.left)
                if node.right:
                    stack.append(node.right)
                cur.next = ListNode(node.val)
                    
                cur=cur.next
            res.append(head.next)
        return res


def listOfDepth(self, tree: TreeNode) -> List[ListNode]:
        if not tree: return []
        from collections import deque
        layer = deque()
        layer.append(tree)
        res = []

        while layer:
            cur = dummy = ListNode(0)
            for _ in range(len(layer)):
                node = layer.popleft()
                cur.next = ListNode(node.val)
                cur = cur.next

                if node.left:
                    layer.append(node.left)
                if node.right:
                    layer.append(node.right)
            res.append(dummy.next)
        return res



def listOfDepth(self, tree: TreeNode) -> List[ListNode]:
        if tree == None: #特判
            return([])
        answer = [[tree.val]]
        queue = ['a',tree] #初始化队列
        while queue:
            a = queue.pop(0)
            if a == 'a':
                queue.append('a')
                answer.append([])
            else:
                if a.left:
                    queue.append(a.left)
                    answer[-1].append(a.left.val)
                if a.right:
                    queue.append(a.right)
                    answer[-1].append(a.right.val)
            if len(queue) == 1 and queue[-1] == 'a':
                answer.pop(-1)
                break
        answer_final = []
        for i in answer:
            cur = None
            for ind_j,j in enumerate(i):
                if ind_j == 0:#head = cur = ListNode(j) #这里必须用连等，如果用cur = Listnode(j),head = ListNode(j)的情况下，head.next不能通过cur.next赋值,未知原因
                    head = cur = ListNode(j)
                    '''或：
                    head = ListNode(j)
                    cur = head'''
                else:
                    cur.next = ListNode(j)
                    cur = cur.next
            answer_final.append(head)
        return(answer_final)


def listOfDepth(self, tree: TreeNode) -> List[ListNode]:
        if not tree:
            return []
        stack = [tree]
        res = []
        dummy = ListNode(-1)
        while stack:
            n = len(stack)
            tmp = dummy
            while n > 0:
                elt = stack.pop(0)
                n -= 1
                tmp.next = ListNode(elt.val)
                tmp = tmp.next
                if elt.left:
                    stack.append(elt.left)
                if elt.right:
                    stack.append(elt.right)
            res.append(dummy.next)
            dummy.next = None
        return res



def listOfDepth(self, tree: TreeNode) -> List[ListNode]:
        if tree is None:
            return 
        ret=[]
        ret_tail=[]
        arr=[(tree,0)]
        while arr:
            cur,deep=arr.pop(0)
            if cur.left:
                arr.append((cur.left,deep+1))
            if cur.right:
                arr.append((cur.right,deep+1))
            node=ListNode(cur.val)
            if len(ret)>deep:
                ret_tail[deep].next=node
                ret_tail[deep]=node
            else:
                ret.append(node)
                ret_tail.append(node)
        return ret



def listOfDepth(self, tree: TreeNode) -> List[ListNode]:
    res,temp=[],[]
    
    def list2link(s):
        head=ListNode(10000)
        cur=head
        for i in s:
            cur.next=ListNode(i)
            cur=cur.next
        return head.next

    def bfs(node):
        queue=[(node,0)]
        while(len(queue)!=0):
            cur,level=queue.pop()

            if cur==None:
                continue
            res.append((cur,level))
            queue.insert(0,(cur.left,level+1))
            queue.insert(0,(cur.right,level+1))
    bfs(tree)

    temp=[[] for _ in range(max(res,key=lambda i:i[1])[1]+1)]
    for r in res:
        temp[r[1]].append(r[0].val)
    # print(temp)
    for p in range(len(temp)):
        temp[p]=list2link(temp[p])

    return temp


def listOfDepth(self, tree: TreeNode) -> List[ListNode]:
    ans = []
    queue = deque()
    queue.appendleft((tree, 1))
    d = {}
    while queue:
        t, dep = queue.pop()
        if dep not in d.keys():
            if dep - 1 in d.keys():
                ans.append(d[dep - 1])
            d[dep] = ListNode(t.val)
        else:
            l = d[dep]
            while l.next:
                l = l.next
            l.next = ListNode(t.val)
        if t.left:
            queue.appendleft((t.left, dep + 1))
        if t.right:
            queue.appendleft((t.right, dep + 1))
    ans.append(d[dep])
    return ans


 def listOfDepth(self, tree: TreeNode) -> List[ListNode]:
        head, trees = ListNode(0), tree and [tree]
        while trees:
            tmp = head
            for tree in trees:
                tmp.next = ListNode(tree.val)
                tmp = tmp.next
            yield head.next
            trees = [leave for tree in trees for leave in (tree.left, tree.right) if leave]


























