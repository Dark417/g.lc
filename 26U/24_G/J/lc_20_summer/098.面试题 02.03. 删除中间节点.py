"""
098.面试题 02.03. 删除中间节点

实现一种算法，删除单向链表中间的某个节点（即不是第一个或最后一个节点），假定你只能访问该节点。

 

示例：

输入：单向链表a->b->c->d->e->f中的节点c
结果：不返回任何数据，但该链表变为a->b->d->e->f

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/delete-middle-node-lcci
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

"""


def deleteNode(self, node):
	node.val = node.next.val
	node.next = node.next.next


def deleteNode(self, node: ListNode, n: int) -> None:
    while True:
        if node.val == n:
            node.val = node.next.val
            node.next = node.next.next
            break
        else:
            node = node.next



def deleteNode(self, node):
    if not node or not node.next:
        return
    
    # 保存将要被删除的节点，防止删除之后找不到
    dummy = node.next
    # 删除当前节点的下一个节点
    node.next = node.next.next
    # 将已经被删除掉的下一个节点的值赋值给真实需要被删除的节点
    node.val = dummy.val



def deleteNode(self, node):
    while node.next:
         node.val = node.next.val
         if not node.next.next:
             node.next = None
             break
         node = node.next









































