"""
115.234. Palindrome Linked List
面试题 02.06. 回文链表


编写一个函数，检查输入的链表是否是回文的。

 

示例 1：

输入： 1->2
输出： false 
示例 2：

输入： 1->2->2->1
输出： true 


write functions


"""

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



def isPalindrome(self, head: ListNode) -> bool:
    if head is None:
        return True

    # 找到前半部分链表的尾节点并反转后半部分链表
    first_half_end = self.end_of_first_half(head)
    second_half_start = self.reverse_list(first_half_end.next)

    # 判断是否回文
    result = True
    first_position = head
    second_position = second_half_start
    while result and second_position is not None:
        if first_position.val != second_position.val:
            result = False
        first_position = first_position.next
        second_position = second_position.next

    # 还原链表并返回结果
    first_half_end.next = self.reverse_list(second_half_start)
    return result    

def end_of_first_half(self, head):
    fast = head
    slow = head
    while fast.next is not None and fast.next.next is not None:
        fast = fast.next.next
        slow = slow.next
    return slow

def reverse_list(self, head):
    previous = None
    current = head
    while current is not None:
        next_node = current.next
        current.next = previous
        previous = current
        current = next_node
    return previous



# Stefan

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
    rev = None
    fast = head
    while fast and fast.next:
        fast = fast.next.next
        rev, rev.next, head = head, rev, head.next
    tail = head.next if fast else head
    isPali = True
    while rev:
        isPali = isPali and rev.val == tail.val
        head, head.next, rev = rev, head, rev.next
        tail = tail.next
    return isPali



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



# D
def isPalindrome(self, head: ListNode) -> bool:
	if not head: return True
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    
    cur = slow
    #pre = ListNode(None)	# val is None
    pre = None

    while cur:
        next = cur.next
        cur.next = pre
        pre = cur
        cur = next
    s.next = None

    while head and pre:
        if head.val != pre.val:
            return False
        head = head.next
        pre = pre.next
    return True


def isPalindrome(self, head: ListNode) -> bool:
    l = []
    while head:
        l.append(head.val)
        head = head.next
    return l == l[::-1]


def isPalindrome(self, head: ListNode) -> bool:
    if not head or not head.next: return True

    slow = fast = head
    while fast and fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    pre = ListNode(0)
    end = cur = slow.next
    while cur:
        next = cur.next
        cur.next = pre
        pre = cur
        cur = next
    end.next = None

    while head and pre:
        if head.val == pre.val:
            head = head.next
            pre = pre.next
        else:
            return False
    return True

























































