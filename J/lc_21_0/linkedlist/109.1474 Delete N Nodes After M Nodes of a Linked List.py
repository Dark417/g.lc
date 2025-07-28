"""
109.1474 Delete N Nodes After M Nodes of a Linked List
删除链表 M 个节点之后的 N 个节点

给定链表 head 和两个整数 m 和 n. 遍历该链表并按照如下方式删除节点:

开始时以头节点作为当前节点.
保留以当前节点开始的前 m 个节点.
删除接下来的 n 个节点.
重复步骤 2 和 3, 直到到达链表结尾.
在删除了指定结点之后, 返回修改过后的链表的头节点.

进阶问题: 你能通过就地修改链表的方式解决这个问题吗?

 

示例 1:



输入: head = [1,2,3,4,5,6,7,8,9,10,11,12,13], m = 2, n = 3
输出: [1,2,6,7,11,12]
解析: 保留前(m = 2)个结点,  也就是以黑色节点表示的从链表头结点开始的结点(1 ->2).
删除接下来的(n = 3)个结点(3 -> 4 -> 5), 在图中以红色结点表示.
继续相同的操作, 直到链表的末尾.
返回删除结点之后的链表的头结点.
示例 2:



输入: head = [1,2,3,4,5,6,7,8,9,10,11], m = 1, n = 3
输出: [1,5,9]
解析: 返回删除结点之后的链表的头结点.
示例 3:

输入: head = [1,2,3,4,5,6,7,8,9,10,11], m = 3, n = 1
输出: [1,2,3,5,6,7,9,10,11]
示例 4:

输入: head = [9,3,7,7,9,10,8,2], m = 1, n = 2
输出: [9,7,8]
 

提示:

 1 <= 链表结点数 <= 10^4.
[1 <= 链表的每一个结点值 <=10^6].
1 <= m,n <= 1000

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/delete-n-nodes-after-m-nodes-of-a-linked-list
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

"""


def deleteNodes(self, head: ListNode, m: int, n: int) -> ListNode:
    if not head: return None
    cur  = head
    while cur:
        i = 0
        while i < m:
            if cur:
                pre = cur
                cur = cur.next
                i += 1
            else:
                return head
        if i == m:
            i = 0
            while i < n:
                if cur:
                    cur = cur.next
                    i += 1
                else:
                    pre.next = None
                    return head
            if i == n:
                pre.next = cur
            else:
                break
        else:
            break
    return head



def deleteNodes(self, head: ListNode, m: int, n: int) -> ListNode:
    dummy = ListNode(0)
    dummy.next = head
    cur = dummy
    while cur.next:
        p,q = m,n
        while p > 0 and cur.next:
            p -= 1
            cur = cur.next
        while q > 0 and cur.next:     
            q -= 1
            cur.next = cur.next.next   # 直接改变cur的后继结点。
    return dummy.next



def deleteNodes(self, head: ListNode, m: int, n: int) -> ListNode:
    dummy = ListNode(0)
    dummy.next = head
    cur = dummy
    while cur.next:
        p,q = m,n
        while p and cur.next:
            cur = cur.next
            p-=1
        while q and cur.next:
            cur.next = cur.next.next
            q-=1
    return dummy.next


def deleteNodes(self, head: ListNode, m: int, n: int) -> ListNode:
    fake = ListNode(0)
    fake.next = head
    cur = fake
    while True:
        i = 0
        while i < m and cur.next:
            cur, i = cur.next, i+1
        if i < m:
            break

        i = 0
        while i < n and cur.next:
            tmp = cur.next.next
            cur.next.next = None
            cur.next = tmp
            i += 1

        if i < n:
            break
    
    ans = fake.next
    fake.next = None
    return ans


def deleteNodes(self, head: ListNode, m: int, n: int) -> ListNode:
    if not head: return None
    res = ListNode(None)  # 构造一个哑节点
    node = res            # 用于移动的节点
    i = 0
    while head:
        i += 1
        if 0 < i % (m+n) <= m:
            node.next = head
            node = node.next
        head = head.next
    node.next = None      # 链尾指向空
    return res.next
















def deleteNodes(self, head: ListNode, m: int, n: int) -> ListNode:
    if not head: return None
    a = b = head
    c, d = m, n
    while m-1 and a.next:
        a, b = a.next, b.next
        m -=1
    while n and b.next:
        b = b.next
        n-=1
    a.next = self.deleteNodes(b.next, c, d)

    return head


。





































