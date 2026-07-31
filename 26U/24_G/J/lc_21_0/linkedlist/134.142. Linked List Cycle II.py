"""
134.142. Linked List Cycle II
环形链表 II

Given a linked list, return the node where the cycle begins. If there is no cycle, 
return null.

To represent a cycle in the given linked list, we use an integer pos which represents 
the position (0-indexed) in the linked list where tail connects to. If pos is -1, then there is no cycle in the linked list.

Note: Do not modify the linked list.

 

Example 1:

Input: head = [3,2,0,-4], pos = 1
Output: tail connects to node index 1
Explanation: There is a cycle in the linked list, where tail connects to the second node.


Example 2:

Input: head = [1,2], pos = 0
Output: tail connects to node index 0
Explanation: There is a cycle in the linked list, where tail connects to the first node.


Example 3:

Input: head = [1], pos = -1
Output: no cycle
Explanation: There is no cycle in the linked list.


 

Follow-up:
Can you solve it without using extra space?

"""

def detectCycle(self, head: ListNode) -> ListNode:
    s = set()
    cur = head
    while cur:
        if cur not in s:
            s.add(cur)
        else:
            return cur
        cur = cur.next
    return None



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





















