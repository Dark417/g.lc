"""
140.328	Odd Even Linked List
奇偶链表


Given a singly linked list, group all odd nodes together followed by the even nodes. Please note here we are talking about the node number and not the value in the nodes.

You should try to do it in place. The program should run in O(1) space complexity and O(nodes) time complexity.

Example 1:

Input: 1->2->3->4->5->NULL
Output: 1->3->5->2->4->NULL
Example 2:

Input: 2->1->3->5->6->4->7->NULL
Output: 2->3->6->7->1->5->4->NULL
 

Constraints:

The relative order inside both the even and odd groups should remain as it was in the input.
The first node is considered odd, the second node even and so on ...
The length of the linked list is between [0, 10^4].

"""


def oddEvenList(self, head: ListNode) -> ListNode:
	if not head: return None
	odd = head
	even = h = head.next
	while even and even.next:
		odd.next = even.next
		odd = odd.next
		even.next = odd.next
		even = even.next
	odd.next = h
	return head




def oddEvenList(self, head: ListNode) -> ListNode:
    if not head:return head
    odd = head
    even_head = even = head.next
    while odd.next and even.next:
        odd.next = odd.next.next
        even.next = even.next.next
        odd,even = odd.next,even.next
    odd.next = even_head
    return head



def oddEvenList(self, head: ListNode) -> ListNode:
    change = head
    pre = head
    cur = head
    while pre and pre.next and pre.next.next:
        cur = pre.next.next
        pre = pre.next            
        
        pre.next = cur.next
        cur.next = change.next
        change.next = cur
        change = change.next        
    return head



def oddEvenList(self, head):
    dummy1 = odd = ListNode(0)
    dummy2 = even = ListNode(0)
    while head:
        odd.next = head
        even.next = head.next
        odd = odd.next
        even = even.next
        head = head.next.next if even else None
    odd.next = dummy2.next
    return dummy1.next



def oddEvenList(self, head):
    d1=odd=ListNode(0)
    d2=even=ListNode(0)
    i=1
    while head:
        if i%2:
            odd.next,odd=head,head
        else:
            even.next,even=head,head
        head=head.next
        i+=1
    odd.next,even.next=d2.next,None
    return d1.next


def oddEvenList(self, head):
    odd, even = tail = [ListNode(0), ListNode(0)]
    i = 0
    while head:
        tail[i].next = tail[i] = head
        head = head.next
        i ^= 1
    tail[0].next = even.next
    tail[1].next = None
    return odd.next



def oddEvenList(self, head):
    if head:
        odd = head
        even = evenHead = odd.next
        while even and even.next:
            odd.next = odd = even.next
            even.next = even = odd.next
        odd.next = evenHead
        return head



def oddEvenList(self, head):
    odd, p= head, head and head.next 
    while p and p.next:
        odd.next, p.next.next, p.next = p.next, odd.next, p.next.next #insert 
        odd, p = odd.next, p.next 
    return head



def oddEvenList(self, head: ListNode) -> ListNode:
    if head == None: return None
    def getOdds(head):
        first = head
        second = head.next
        if head.next == None or head.next.next == None:
            return ListNode(head.val),head.next
        odd1,odd2 = getOdds(head.next.next)
        first.next = odd1
        second.next = odd2
        return first,second
    first,second = getOdds(head)
    curr = first
    while curr.next != None:
        curr = curr.next
    curr.next = second
    return first



def oddEvenList(self, head: ListNode) -> ListNode:
    dummy_odd = odd = ListNode(None)
    dummy_even = even = ListNode(None)

    def recursive(head, idx):
        nonlocal odd, even
        if head is None:
            return

        if idx % 2:  # odd
            odd.next = head
            odd = odd.next
        else:
            even.next = head
            even = even.next

        recursive(head.next, idx + 1)
        return

    recursive(head, 1)
    even.next = None
    odd.next = dummy_even.next
    return dummy_odd.next
































