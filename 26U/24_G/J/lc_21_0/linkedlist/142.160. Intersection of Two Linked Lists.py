"""
142.160. Intersection of Two Linked Lists 相交链表
相交链表
剑指 Offer 52. 两个链表的第一个公共节点

Write a program to find the node at which the intersection of two singly linked lists begins.

For example, the following two linked lists:


begin to intersect at node c1.

 

Example 1:


Input: intersectVal = 8, listA = [4,1,8,4,5], listB = [5,6,1,8,4,5], skipA = 2, skipB = 3
Output: Reference of the node with value = 8
Input Explanation: The intersected node's value is 8 (note that this must not be 0 if the two lists 
intersect). From the head of A, it reads as [4,1,8,4,5]. From the head of B, it reads as [5,6,1,8,4,5]. 
There are 2 nodes before the intersected node in A; There are 3 nodes before the intersected node in B.
 

Example 2:


Input: intersectVal = 2, listA = [1,9,1,2,4], listB = [3,2,4], skipA = 3, skipB = 1
Output: Reference of the node with value = 2
Input Explanation: The intersected node's value is 2 (note that this must not be 0 if the two lists intersect). 
From the head of A, it reads as [1,9,1,2,4]. From the head of B, it reads as [3,2,4]. 
There are 3 nodes before the intersected node in A; There are 1 node before the intersected node in B.
 

Example 3:


Input: intersectVal = 0, listA = [2,6,4], listB = [1,5], skipA = 3, skipB = 2
Output: null
Input Explanation: From the head of A, it reads as [2,6,4]. From the head of B, it reads as [1,5]. 
Since the two lists do not intersect, intersectVal must be 0, while skipA and skipB can be arbitrary values.
Explanation: The two lists do not intersect, so return null.
 

Notes:

If the two linked lists have no intersection at all, return null.
The linked lists must retain their original structure after the function returns.
You may assume there are no cycles anywhere in the entire linked structure.
Each value on each linked list is in the range [1, 10^9].
Your code should preferably run in O(n) time and use only O(1) memory.


对链表A中的每一个结点 a_ia 
i
​	
 ，遍历整个链表 B 并检查链表 B 中是否存在结点和 a_ia 
i
​	
  相同。

复杂度分析

时间复杂度 : (mn)(mn)。
空间复杂度 : O(1)O(1)。


遍历链表 A 并将每个结点的地址/引用存储在哈希表中。然后检查链表 B 中的每一个结点 b_ib 
i 是否在哈希表中。若在，则 b_ibi 为相交结点。

复杂度分析

时间复杂度 : O(m+n)O(m+n)。
空间复杂度 : O(m)O(m) 或 O(n)O(n)。



方法三：双指针法
创建两个指针 pApA 和 pBpB，分别初始化为链表 A 和 B 的头结点。然后让它们向后逐结点遍历。
当 pApA 到达链表的尾部时，将它重定位到链表 B 的头结点 (你没看错，就是链表 B); 类似的，当 pBpB 到达链表的尾部时，将它重定位到链表 A 的头结点。
若在某一时刻 pApA 和 pBpB 相遇，则 pApA/pBpB 为相交结点。
想弄清楚为什么这样可行, 可以考虑以下两个链表: A={1,3,5,7,9,11} 和 B={2,4,9,11}，相交于结点 9。 由于 B.length (=4) < A.length (=6)，pBpB 比 pApA 少经过 22 个结点，会先到达尾部。将 pBpB 重定向到 A 的头结点，pApA 重定向到 B 的头结点后，pBpB 要比 pApA 多走 2 个结点。因此，它们会同时到达交点。
如果两个链表存在相交，它们末尾的结点必然相同。因此当 pApA/pBpB 到达链表结尾时，记录下链表 A/B 对应的元素。若最后元素不相同，则两个链表不相交。
复杂度分析

时间复杂度 : O(m+n)O(m+n)。
空间复杂度 : O(1)O(1)。









"""

def getIntersectionNode(self, headA, headB):
    if headA is None or headB is None:
        return None

    pa = headA # 2 pointers
    pb = headB

    while pa is not pb:
        # if either pointer hits the end, switch head and continue the second traversal, 
        # if not hit the end, just move on to next
        pa = headB if pa is None else pa.next
        pb = headA if pb is None else pb.next

    return pa



def getIntersectionNode(self, headA, headB):
    a, b = headA, headB
    while a != b:
        a = a.next if a else headB
        b = b.next if b else headA
    return a

def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> ListNode:
    h1, h2 = headA, headB
    res = h1
    while h1:
        while h2:
            if h1 == h2:
                res = h2
                return res
            else:
                h2 = h2.next
        h2 = headB
        h1 = h1.next
    return None


def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> ListNode:
    h1, h2 = headA, headB
    while h1 != h2:
        h1 = h1.next if h1 else headB
        h2 = h2.next if h2 else headA
    return h1






def getIntersectionNode(self, headA, headB):
    p1, p2 = headA, headB
    while p1 != p2:
        p1 = headB if not p1 else p1.next
        p2 = headA if not p2 else p2.next
    return p1


def getIntersectionNode(self, headA, headB):
    if headA and headB:
        A, B = headA, headB
        while A!=B:
            A = A.next if A else headB
            B = B.next if B else headA
        return A


def getIntersectionNode1(self, headA, headB):
    if not headA or not headB: return None
    
    pA, pB = headA, headB
    while pA and pB:
        if pA == pB:
            return pA

        pA, pB = pA.next, pB.next
        if not pA and not pB: return None
        
        if not pA: pA = headB
        if not pB: pB = headA
    
    return None



def getIntersectionNode(self, A, B):
    if not A or not B: return None

    # Concatenate A and B
    last = A
    while last.next: last = last.next
    last.next = B

    # Find the start of the loop
    fast = slow = A
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow == fast:
            fast = A
            while fast != slow:
                slow, fast = slow.next, fast.next
            last.next = None
            return slow

    # No loop found
    last.next = None
    return None



def getIntersectionNode(self, headA, headB):
    curA,curB = headA,headB
    lenA,lenB = 0,0
    while curA is not None:
        lenA += 1
        curA = curA.next
    while curB is not None:
        lenB += 1
        curB = curB.next
    curA,curB = headA,headB
    if lenA > lenB:
        for i in range(lenA-lenB):
            curA = curA.next
    elif lenB > lenA:
        for i in range(lenB-lenA):
            curB = curB.next
    while curB != curA:
        curB = curB.next
        curA = curA.next
    return curA


def getIntersectionNode(self, headA, headB):
    ptA, ptB, jumpToNext = headA, headB, False
    while ptA and ptB:
        if ptA == ptB:
            return ptA
        ptA, ptB = ptA.next, ptB.next
        if not ptA and not jumpToNext:
            ptA, jumpToNext = headB, True
        if not ptB:
            ptB = headA
    return None


def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> ListNode:
    pA,pB=headA,headB
    while pA!=pB:
        if pA:
            pA=pA.next
        else:
            pA=headB
        
        if  pB:
            pB=pB.next
        else:
            pB=headA               
    return pA


def getIntersectionNode(self, headA, headB):
    p, q = headA, headB;
    while p != q:
        p = p.next if p else headB;
        q = q.next if q else headA;
    return p;


def getIntersectionNode(self, headA, headB):
    ha, hb = headA, headB
    while ha != hb:
        ha = ha.next if ha else headB
        hb = hb.next if hb else headA
    return ha
























