
# 21. 合并两个有序链表
def mergeTwoLists(self, l1, l2):
    if l1 is None:
        return l2
    elif l2 is None:
        return l1
    elif l1.val < l2.val:
        l1.next = self.mergeTwoLists(l1.next, l2)
        return l1
    else:
        l2.next = self.mergeTwoLists(l1, l2.next)
        return l2


def mergeTwoLists(self, l1, l2):
    prehead = ListNode(-1)
    prev = prehead
    while l1 and l2:
        if l1.val <= l2.val:
            prev.next = l1
            l1 = l1.next
        else:
            prev.next = l2
            l2 = l2.next            
        prev = prev.next

    prev.next = l1 if l1 is not None else l2
    return prehead.next


# 206. 反转链表
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




# 237. 删除链表中的节点
def deleteNode(self, node):
    node.val = node.next.val
    node.next = node.next.next




# 203. 移除链表元素
def removeElements(self, head: ListNode, val: int) -> ListNode:
    if not head:
        return None
    head.next = self.removeElements(head.next, val)
    if head.val == val:
        return head.next
    else:
        return head


def removeElements(self, head: ListNode, val: int) -> ListNode:
    sentinel = ListNode(0)
    sentinel.next = head
    
    prev, curr = sentinel, head
    while curr:
        if curr.val == val:
            prev.next = curr.next
        else:
            prev = curr
        curr = curr.next
    
    return sentinel.next


def removeElements(self, head: ListNode, val: int) -> ListNode:
    while head and head.val == val:
        head = head.next
    if not head:
        return head
    pre = head
    while pre.next:
        if pre.next.val == val:
            pre.next = pre.next.next
        else:
            pre = pre.next
    return head


# 83. 移除重复节点
#iter, set, recur
def deleteDuplicates(self, head: ListNode) -> ListNode:
    cur = head
    while cur and cur.next:
        if cur.next.val == cur.val:
            cur.next = cur.next.next
        else:
            cur = cur.next
    return head

def deleteDuplicates(self, head: ListNode) -> ListNode:
    if head and head.next:
        head.next = self.deleteDuplicates(head.next)
        return head.next if head.next.val == head.val else head
    return head



# 234. 回文链表
def isPalindrome(self, head: ListNode) -> bool:
    self.front_pointer = head

    def recursively_check(current_node=head):
        if current_node is not None:
            if not recursively_check(current_node.next):
                return False
            if self.front_pointer.val != current_node.val:
                return False
            self.front_pointer = self.front_pointer.next
        return True

    return recursively_check()








# 876. 链表的中间结点
# https://leetcode-cn.com/problems/middle-of-the-linked-list/solution/kuai-man-zhi-zhen-zhu-yao-zai-yu-diao-shi-by-liwei/
# old, slow at mid, fast at end; 
# even, slow at mid+1, fast at null;
def middleNode(self, head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow

# old, slow at mid, fast at end; 
# even, slow at mid-1, fast at ??;
def middleNode(self, head):
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    return slow.next



def isPalindrome(self, head):
    rev = None
    slow = fast = head
    while fast and fast.next:
        fast = fast.next.next
        rev, rev.next, slow = slow, rev, slow.next
    if fast:
        slow = slow.next
    while rev and rev.val == slow.val:
        slow = slow.next
        rev = rev.next
    return not rev


def isPalindrome(self, head):
    fast = slow = head
    # find the mid node
    while fast and fast.next:
        fast = fast.next.next
        slow = slow.next
    # reverse the second half
    node = None
    while slow:
        nxt = slow.next
        slow.next = node
        node = slow
        slow = nxt
    # compare the first and second half nodes
    while node: 	# while node and head:		# 2nd from n/2+1
        if node.val != head.val:
            return False
        node = node.next
        head = head.next
    return True





# 141.环 形链表
def hasCycle(self, head: ListNode) -> bool:
    s = set()
    while head:
        if head not in s:
            s.add(head)
        else:
            return True
        head = head.next
    return False


def hasCycle(self, head: ListNode) -> bool:
    if not head or not head.next:
        return False
    slow = head
    fast = head.next

    while slow != fast:
        if not fast or not fast.next:
            return False
        slow = slow.next
        fast = fast.next.next
    return True



def hasCycle(self, head):
    while head:
        if head.val == None:
            return True
        head.val = None
        head = head.next
    return False


def hasCycle(self, head):
    slow = fast = head
    while fast and fast.next:
        fast = fast.next.next
        slow = slow.next
        if slow == fast:
            return True
    return False



# 142. 环形链表 II
def detectCycle(self, head):
    fast, slow = head, head
    while True:
        if not (fast and fast.next): return
        fast, slow = fast.next.next, slow.next
        if fast == slow: break
    fast = head
    while fast != slow:
        fast, slow = fast.next, slow.next
    return fast



def detectCycle(self, head):
    fast = slow = head
    while fast and fast.next:
        fast = fast.next.next
        slow = slow.next
        # if there is a cycle
        if slow is fast:
            # the head and slow nodes move step by step
            while head:
                if head == slow:
                    return head
                head = head.next
                slow = slow.next
    return None



# 160. 链表相交
def getIntersectionNode(self, headA, headB):
    a, b = headA, headB
    while a != b:
        a = a.next if a else headB
        b = b.next if b else headA
    return a



# 剑指 Offer 22. 链表中倒数第k个节点
def kthToLast(self, head: ListNode, k: int) -> int:
    start = end = head
    for i in range(k):
        end = end.next 
    while end:
        head = head.next
        end = end.next
    return head.val


# 1290. Convert Binary Number in a Linked List to Integer 二进制链表转整数
# https://leetcode-cn.com/problems/convert-binary-number-in-a-linked-list-to-integer/solution/4chong-fang-fa-zhi-jie-bian-li-di-gui-zhan-arrayli/
def getDecimalValue(self, head: ListNode) -> int:
    res = 0
    while head:
        res = res*2 + head.val
        head = head.next
    return res



# 1474. 删除链表 M 个节点之后的 N 个节点
def deleteNodes(self, head: ListNode, m: int, n: int) -> ListNode:
    dum = cur = ListNode(0)
	dum.next = head
    cur = dum
    while cur.next:
        p, q = m, n
        while p > 0 and cur.next:
            cur = cur.next
            p -= 1
        while q > 0 and cur.next:
            q -= 1
            cur.next = cur.next.next
    return dum.next







########################################################
#mid



# 2. 两数相加
def addTwoNumbers(self, l1, l2):
    dummy = cur = ListNode(0)
    carry = 0
    while l1 or l2 or carry:
        if l1:
            carry += l1.val
            l1 = l1.next
        if l2:
            carry += l2.val
            l2 = l2.next
        cur.next = ListNode(carry%10)
        cur = cur.next
        carry //= 10
    return dummy.next




# 445. Add Two Numbers II 两数相加 II
def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
    s1, s2 = [], []
    while l1:
        s1.append(l1.val)
        l1 = l1.next
    while l2:
        s2.append(l2.val)
        l2 = l2.next
    ans = None
    carry = 0
    while s1 or s2 or carry != 0:
        a = 0 if not s1 else s1.pop()
        b = 0 if not s2 else s2.pop()
        cur = a + b + carry
        carry = cur // 10
        cur %= 10
        curnode = ListNode(cur)
        curnode.next = ans
        ans = curnode
    return ans









































# 1171. 从链表中删去总和值为零的连续节点
def numComponents(self, head: ListNode, G: List[int]) -> int:
    ans, G = 0, set(G)
    while head:
        if head.val in G:
            if not head.next or head.next.val not in G:
                ans += 1
        head = head.next
    return ans







# 1721. 交换链表中的节点
def swapNodes(self, head: ListNode, k: int) -> ListNode:
    slow, fast = head, head
    for _ in range(k - 1):
        fast = fast.next
    first = fast
    while fast.next:
        slow, fast = slow.next, fast.next
    first.val, slow.val = slow.val, first.val
    return head

def swapNodes(self, head: ListNode, k: int) -> ListNode:
    p,q,n=head,head,head
    i=1
    while n:
        if i<k:
            p=p.next#正数第k个
        if i>k:
            q=q.next#倒数第k个
        n=n.next
        i+=1
    p.val,q.val=q.val,p.val
    return head

def swapNodes(self, head: ListNode, k: int) -> ListNode:
    n1, n2, p = None, None, head
    while p is not None:
        k -= 1
        n2 = None if n2 == None else n2.next
        if k == 0:
            n1 = p
            n2 = head
        p = p.next
    n1.val, n2.val = n2.val, n1.val
    return head


































































