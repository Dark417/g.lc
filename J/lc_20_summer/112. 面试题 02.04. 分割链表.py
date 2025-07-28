"""
112. 面试题 02.04. 分割链表

编写程序以 x 为基准分割链表，使得所有小于 x 的节点排在大于或等于 x 的节点之前。如果链表中包含 
x，x 只需出现在小于 x 的元素之后(如下所示)。分割元素 x 只需处于“右半部分”即可，
其不需要被置于左右两部分之间。

示例:

输入: head = 3->5->8->5->10->2->1, x = 5
输出: 3->1->2->10->5->5->8

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/partition-list-lcci
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

"""

def partition(self, head: ListNode, x: int) -> ListNode:
    def getMiddle(h:ListNode):
        if h.next:
            slow,fast = h,h.next
            while fast.next:
                slow = slow.next
                fast = fast.next.next
                if not fast:
                    return slow
            return slow
        else:
            return h

    def mergeTwoSortedLists(l1,l2):
        dummy = pre = ListNode(0)
        while l1 and l2:
            if l1.val < l2.val:
                pre.next = l1
                l1 = l1.next
            else:
                pre.next = l2
                l2 = l2.next
            pre = pre.next
        pre.next = l1 or l2
        return dummy.next

    def mergeSort(node):
        if not node:
            return None
        if not node.next:
            return node
        if not node.next.next:
            if node.val > node.next.val:
                node.val,node.next.val = node.next.val,node.val
            return node
        else:
            midpre = getMiddle(node)
            middle,midpre.next = midpre.next,None
            return mergeTwoSortedLists(mergeSort(middle),mergeSort(node))
    return mergeSort(head)



def partition(self, head: ListNode, x: int) -> ListNode:
    p, q = head, head
    while q:
        if q.val < x:
            q.val, p.val = p.val, q.val
            p = p.next
        q = q.next
    return head


def partition(self, head: ListNode, x: int) -> ListNode:
    before =before_head = ListNode(0)
    after = after_head = ListNode(0)
    while head:
        if head.val < x:
            before.next=head  #before_head的下一个指向head
            before=before.next
        else:
            after.next=head
            after=after.next

        head=head.next
    after.next=None  #将after尾部指向空
    before.next=after_head.next  #将before的下一个指向after_head的下一个

    return before_head.nex


# 双链表法
def partition(self, head: ListNode, x: int) -> ListNode:
    l1 = p = ListNode(-1)
    l2 = q = ListNode(-1)
    while head:
        if head.val < x:
            p.next = head
            p = p.next
        else:
            q.next = head
            q = q.next
        head = head.next
    p.next, q.next = l2.next, None
    return l1.next  


# 交换法
def partition(self, head: ListNode, x: int) -> ListNode:
    pre, cur = head, head
    while cur:
        if cur.val < x:
            pre.val, cur.val = cur.val, pre.val
            pre = pre.next
        cur = cur.next
    return head 


# 头插法
def partition(self, head: ListNode, x: int) -> ListNode:
    dummy = ListNode(-1, head)
    pre, cur = dummy, head
    while cur:
        if cur.val < x and head != cur:
            pre.next = cur.next
            cur.next = dummy.next
            dummy.next = cur
            cur = pre.next
        else:                                                                                
            pre = pre.next
            cur = cur.next
    return dummy.next 




def partition(self, head: ListNode, x: int) -> ListNode:
    tmp = []
    i = head 
    while i:
        tmp.append(i.val)
        i = i.next 
    tmp.sort(reverse=True)
    i = head 
    while i:
        i.val = tmp.pop()
        i = i.next 
    return head 


def partition(self, head: ListNode, x: int) -> ListNode:
    part1, part2 = [], []
    i = head 
    while i:
        if i.val<x:
            part1.append(i.val)
        else:
            part2.append(i.val)
        i = i.next 
    i = head 
    while i:
        if part1:
            i.val = part1.pop()
        elif part2:
            i.val = part2.pop()
        i = i.next 
    return head 

def partition(self, head: ListNode, x: int) -> ListNode:
    i, j = head, head
    while i and j :
        if i.val < x:
            i = i.next 
        else:
            if j == head:
                if i.next:
                    j = i.next #第一次从i后面的节点开始寻找值小于x的节点
            if j is not None and j.val < x: #找到则交换i，j节点的值, i,j指针后移
                i.val, j.val = j.val, i.val 
                i = i.next 
        j = j.next 
    return head
























































