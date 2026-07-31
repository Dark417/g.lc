# 138. 复制带随机指针的链表


def __init__(self):
       self.visitedHash = {}
def copyRandomList(self, head):
    if head == None:
        return None
    if head in self.visitedHash:
        return self.visitedHash[head]
    node = Node(head.val, None, None)
    self.visitedHash[head] = node
    node.next = self.copyRandomList(head.next)
    node.random = self.copyRandomList(head.random)
    return node



def __init__(self):
    self.visited = {}

def getClonedNode(self, node):
    if node:
        if node in self.visited:
            return self.visited[node]
        else:
            self.visited[node] = Node(node.val, None, None)
            return self.visited[node]
    return None

def copyRandomList(self, head):
    if not head:
        return head

    old_node = head
    new_node = Node(old_node.val, None, None)
    self.visited[old_node] = new_node

    while old_node != None:
        new_node.random = self.getClonedNode(old_node.random)
        new_node.next = self.getClonedNode(old_node.next)
        old_node = old_node.next
        new_node = new_node.next

    return self.visited[head]



def copyRandomList(self, head):
    if not head:
        return head

    ptr = head
    while ptr:
        new_node = Node(ptr.val, None, None)
		new_node.next = ptr.next
        ptr.next = new_node
        ptr = new_node.next

    ptr = head
	while ptr:
        ptr.next.random = ptr.random.next if ptr.random else None
        ptr = ptr.next.next

    ptr_old_list = head # A->B->C
    ptr_new_list = head.next # A'->B'->C'
    head_old = head.next
    while ptr_old_list:
        ptr_old_list.next = ptr_old_list.next.next
        ptr_new_list.next = ptr_new_list.next.next if ptr_new_list.next else None
        ptr_old_list = ptr_old_list.next
        ptr_new_list = ptr_new_list.next
    return head_old





























