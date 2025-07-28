"""
108.876. Middle of the Linked List
链表的中间结点

Given a non-empty, singly linked list with head node head, return a middle node of linked list.

If there are two middle nodes, return the second middle node.

 

Example 1:

Input: [1,2,3,4,5]
Output: Node 3 from this list (Serialization: [3,4,5])
The returned node has value 3.  (The judge's serialization of this node is [3,4,5]).
Note that we returned a ListNode object ans, such that:
ans.val = 3, ans.next.val = 4, ans.next.next.val = 5, and ans.next.next.next = NULL.
Example 2:

Input: [1,2,3,4,5,6]
Output: Node 4 from this list (Serialization: [4,5,6])
Since the list has two middle nodes with values 3 and 4, we return the second one.
 

Note:

The number of nodes in the given list will be between 1 and 100.

"""
# https://leetcode-cn.com/problems/middle-of-the-linked-list/solution/kuai-man-zhi-zhen-zhu-yao-zai-yu-diao-shi-by-liwei/

def middleNode(self, head: ListNode) -> ListNode:
    if not head.next: return head
    if not head.next.next: return head.next
    a = head
    b = head.next
    while b.next and b.next.next:
        a = a.next
        b = b.next.next
    return a.next


# old, slow at mid, even at end; 
# even, slow at mid+1, even at null;
def middleNode(self, head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow

# old, slow at mid, even at end; 
# even, slow at mid-1, even at ??;
def middleNode(self, head):
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    return slow.next






# official
def middleNode(self, head: ListNode) -> ListNode:
    A = [head]
    while A[-1].next:
        A.append(A[-1].next)
    return A[len(A) // 2]


def middleNode(self, head: ListNode) -> ListNode:
    n, cur = 0, head
    while cur:
        n += 1
        cur = cur.next
    k, cur = 0, head
    while k < n // 2:
        k += 1
        cur = cur.next
    return cur



























