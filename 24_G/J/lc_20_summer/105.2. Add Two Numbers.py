"""
105.2. Add Two Numbers
两数相加


You are given two non-empty linked lists representing two non-negative integers. 
he digits are stored in reverse order and each of their nodes contain a single 
digit. Add the two numbers and return it as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.

Example:

Input: (2 -> 4 -> 3) + (5 -> 6 -> 4)
Output: 7 -> 0 -> 8
Explanation: 342 + 465 = 807.

"""


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


def addTwoNumbers(self, l1, l2):
    carry = 0
    root = n = ListNode(0)
    while l1 or l2 or carry:
        v1 = v2 = 0
        if l1:
            v1 = l1.val
            l1 = l1.next
        if l2:
            v2 = l2.val
            l2 = l2.next
        carry, val = divmod(v1+v2+carry, 10)
        n.next = ListNode(val)
        n = n.next
    return root.next



def addTwoNumbers(self, l1, l2):
    carry = 0;
    res = n = ListNode(0);
    while l1 or l2 or carry:
        if l1:
            carry += l1.val
            l1 = l1.next;
        if l2:
            carry += l2.val;
            l2 = l2.next;
        carry, val = divmod(carry, 10)
        n.next = n = ListNode(val);
    return res.next;



def addTwoNumbers(self, l1, l2):
    carry = 0
    root = n = None
    while l1 or l2 or carry:
        v1 = v2 = 0
        if l1:
            v1 = l1.val
            l1 = l1.next
        if l2:
            v2 = l2.val
            l2 = l2.next
        carry, val = divmod(v1+v2+carry, 10)
        if n != None:
            n.next = ListNode(val)
            n = n.next
        else:
            n = root = ListNode(val)
    return root



def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
    dummy = cur =ListNode(0)
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
        carry //=10
    return dummy.next



def addTwoNumbers(self, l1, l2):
    ret = ListNode(0)
    cur = ret
    add = 0
    
    while l1 or l2 or add:
        val = (l1.val if l1 else 0) + (l2.val if l2 else 0) + add
        add = val / 10
        cur.next = ListNode(val % 10)
        cur = cur.next
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
    return ret.next


def addTwoNumbers(self, l1, l2):
    ret = cur = ListNode(0); val = 0;
    while l1 or l2 or val:
        if l1: val += l1.val; l1 = l1.next;
        if l2: val += l2.val; l2 = l2.next
        cur.next = cur = ListNode(val%10); val //= 10
    return ret.next



def addTwoNumbers(self, l1, l2):
    head = temp = ListNode(0)
    carry = 0
    while l1 or l2 or carry:
        temp1 = l1.val if l1 else 0
        temp2 = l2.val if l2 else 0
        tempSum = temp1 + temp2 + carry
        
        temp.next = ListNode(tempSum % 10)
        temp = temp.next
        carry = tempSum // 10

        if l1:
            l1 = l1.next
        if l2:
            l2 = l2.next
    return head.next




















































