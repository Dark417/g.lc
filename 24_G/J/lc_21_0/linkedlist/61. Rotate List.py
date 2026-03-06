#!/usr/bin/env python
# coding: utf-8

"""
# 61. Rotate List
Medium

Given a linked list, rotate the list to the right by k places, where k is non-negative.

Example 1:

Input: 1->2->3->4->5->NULL, k = 2
Output: 4->5->1->2->3->NULL
Explanation:
rotate 1 steps to the right: 5->1->2->3->4->NULL
rotate 2 steps to the right: 4->5->1->2->3->NULL
Example 2:

Input: 0->1->2->NULL, k = 4
Output: 2->0->1->NULL
Explanation:
rotate 1 steps to the right: 2->0->1->NULL
rotate 2 steps to the right: 1->2->0->NULL
rotate 3 steps to the right: 0->1->2->NULL
rotate 4 steps to the right: 2->0->1->NULL

"""


def rotateRight(self, head: ListNode, k: int) -> ListNode:
    if not head or not head.next or not k:
        return head
    i = 0
    cur = head
    while cur:
        i += 1
        cur = cur.next
        
    if i == k or k % i == 0:
        return head

    k %= i
    cur = head
    for _ in range(i - k - 1):
        cur = cur.next
    node = cur.next
    cur.next = None
    cur = node
    # while cur and cur.next:
    while cur.next:
        cur = cur.next
    cur.next = head
    return node



def rotateRight(self, head: 'ListNode', k: 'int') -> 'ListNode':
    if not head:
        return None
    if not head.next:
        return head
    
    old_tail = head
    n = 1
    while old_tail.next:
        old_tail = old_tail.next
        n += 1
    old_tail.next = head
    
    new_tail = head
    for i in range(n - k % n - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    
    new_tail.next = None
    
    return new_head




def rotateRight(head, k):
    k = k%len(head)
    output = []
    output[:] = head[k+1:] + head[:k+1]
    return output









































