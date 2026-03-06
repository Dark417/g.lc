"""
133.141. Linked List Cycle
环形链表

Given a linked list, determine if it has a cycle in it.

To represent a cycle in the given linked list, we use an integer pos which represents 
the position (0-indexed) in the linked list where tail connects to. If pos is -1, then there is no cycle in the linked list.

 

Example 1:

Input: head = [3,2,0,-4], pos = 1
Output: true
Explanation: There is a cycle in the linked list, where tail connects to the second node.


Example 2:

Input: head = [1,2], pos = 0
Output: true
Explanation: There is a cycle in the linked list, where tail connects to the first node.


Example 3:

Input: head = [1], pos = -1
Output: false
Explanation: There is no cycle in the linked list.


 

Follow up:

Can you solve it using O(1) (i.e. constant) memory?
"""

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



def hasCycle(self, head: ListNode) -> bool:
    s = set()
    while head:
        if head not in s:
            s.add(head)
        else:
            return True
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



def hasCycle(self, head: ListNode) -> bool:
    while head:
        if head.val == float(inf):
            return True
        head.val = float(inf)
        head = head.next
    return False


def hasCycle(self, head):
    marker1 = head
    marker2 = head
    while marker2!=None and marker2.next!=None:
        marker1 = marker1.next
        marker2 = marker2.next.next
        if marker2==marker1:
            return True
    return False





def hasCycle(self, head):
    try:
        slow = head
        fast = head.next
        while slow is not fast:
            slow = slow.next
            fast = fast.next.next
        return True
    except:
        return False

def hasCycle(self, head):
    if not head:
        return False
    slow = head
    fast = head.next
    while slow is not fast:
        if slow is None or fast is None or fast.next is None:
            return False
        fast = fast.next.next
        slow = slow.next
    return True











































