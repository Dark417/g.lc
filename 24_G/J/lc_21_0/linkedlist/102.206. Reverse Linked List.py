"""
102.206. Reverse Linked List
剑指offer 24. 反转链表


Reverse a singly linked list.

Example:

Input: 1->2->3->4->5->NULL
Output: 5->4->3->2->1->NULL
Follow up:

A linked list can be reversed either iteratively or recursively. 
Could you implement both?

"""

def reverseList(self, head: ListNode) -> ListNode:
    def recur(pre, cur):
        if not cur:
            return pre
        nxt = cur.next
        cur.next = pre
        return recur(cur, nxt)
    
    return recur(None, head)
        
def reverseList(self, head):
    if not head or not head.next: return head
    p = self.reverseList(head.next)
    head.next.next = head
    head.next = None
    return p
    
# iteration

def reverseList(self, head):
	pre = None
	cur = head
	while cur:
		tmp = cur.next
		cur.next = pre
		pre = cur
		cur = tmp
	return pre

def reverseList(self, head):
    cur, prev = head, None
    while cur:
        cur.next, prev, cur = prev, cur, cur.next
    return prev


def reverseList(self, head):
    next=None
    while head:
        head.next,head,next=next,head.next,head
    return next



# recursion

def reverseList(self, head):
    return self._reverse(head)

def _reverse(self, node, prev=None):
    if not node:
        return prev
    n = node.next
    node.next = prev
    return self._reverse(n, node)








def reverseList(self, head):
	if(head==None or head.next==None):
		return head
	# 这里的cur就是最后一个节点
	cur = self.reverseList(head.next)
	# 这里请配合动画演示理解
	# 如果链表是 1->2->3->4->5，那么此时的cur就是5
	# 而head是4，head的下一个是5，下下一个是空
	# 所以head.next.next 就是5->4
	head.next.next = head
	# 防止链表循环，需要将head.next设置为空
	head.next = None
	# 每层递归函数都返回cur，也就是最后一个节点
	return cur






def reverseList(self, head: ListNode) -> ListNode:
    if not head: return None
    l = []
    while head:
        l.append(head)
        head = head.next
    
    l = l[::-1]
    for i in range(len(l)):
        if i == len(l)-1:
            l[i].next = None
        else:
            l[i].next = l[i+1]
    return l[0]


def reverseList(self, head: ListNode) -> ListNode:
    if not head: return None
    l = []
    while head:
        l.append(head)
        head = head.next
    
    for i in range(len(l)-1, -1, -1):
        if i == 0:
            l[i].next = None
        else:
            l[i].next = l[i-1]
    return l[-1]























