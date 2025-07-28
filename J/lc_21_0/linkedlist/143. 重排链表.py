# 143. 重排链表


def reorderList(self, head: ListNode) -> None:
    if not head:
        return
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    l1 = head
    l2 = slow.next
    slow.next = None
    pre = None
    cur = l2
	while cur:
        nxt = cur.next
        cur.next = pre
        pre = cur
        cur = nxt
    while l1 and pre:
        l1next = l1.next
        prenext = pre.next
        l1.next = pre
        pre.next = l1next
        l1 = l1next
        pre = prenext

# shorter / stricter condition
    # while head2:
    #     nextt = head1.next
    #     head1.next = head2
    #     head1 = head2
    #     head2 = nextt


def reorderList(self, head: ListNode) -> None:
    if not head:
        return
    
    mid = self.middleNode(head)
    l1 = head
    l2 = mid.next
    mid.next = None
    l2 = self.reverseList(l2)
    self.mergeList(l1, l2)

def middleNode(self, head: ListNode) -> ListNode:
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    return slow

def reverseList(self, head: ListNode) -> ListNode:
    prev = None
    curr = head
    while curr:
        nextTemp = curr.next
        curr.next = prev
        prev = curr
        curr = nextTemp
    return prev

def mergeList(se`lf, l1: ListNode, l2: ListNode):
    while l1 and l2:
        l1_tmp = l1.next
        l2_tmp = l2.next

        l1.next = l2
        l1 = l1_tmp

        l2.next = l1
        l2 = l2_tmp







def reorderList(self, head: ListNode) -> None:
    if not head:
        return
    
    vec = list()
    node = head
    while node:
        vec.append(node)
        node = node.next
    
    i, j = 0, len(vec) - 1
    while i < j:
        vec[i].next = vec[j]
        i += 1
        if i == j:
            break
        vec[j].next = vec[i]
        j -= 1
    
    vec[i].next = None





"""
public void reorderList(ListNode head) {

    if (head == null || head.next == null || head.next.next == null) {
        return;
    }
    int len = 0;
    ListNode h = head;
    //求出节点数
    while (h != null) {
        len++;
        h = h.next;
    }

    reorderListHelper(head, len);
}

private ListNode reorderListHelper(ListNode head, int len) {
    if (len == 1) {
        ListNode outTail = head.next;
        head.next = null;
        return outTail;
    }
    if (len == 2) {
        ListNode outTail = head.next.next;
        head.next.next = null;
        return outTail;
    }
    //得到对应的尾节点，并且将头结点和尾节点之间的链表通过递归处理
    ListNode tail = reorderListHelper(head.next, len - 2);
    ListNode subHead = head.next;//中间链表的头结点
    head.next = tail;
    ListNode outTail = tail.next;  //上一层 head 对应的 tail
    tail.next = subHead;
    return outTail;
}
"""























