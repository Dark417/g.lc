"""
132.82. Remove Duplicates from Sorted List II 



Given a sorted linked list, delete all nodes that have duplicate numbers, leaving 
only distinct numbers from the original list.

Return the linked list sorted as well.

Example 1:

Input: 1->2->3->3->4->4->5
Output: 1->2->5
Example 2:

Input: 1->1->1->2->3
Output: 2->3

"""


# recursion
def deleteDuplicates(self, head):
    if not head:
        return head
    t = ListNode(None)
    t.next = head
    self.res(head, t, None)
    return t.next

def res(self, this, before, last_value):
    if not this.next:
        if this.val == last_value:
            before.next = None
        return

    if this.val == last_value:
        before.next = this.next

    if this.val != last_value and this.val != this.next.val:
        self.res(this.next, this, this.val)
    else:
        self.res(this.next, before, this.val)




def deleteDuplicates(self, head):
    self.last = t_head = ListNode(None)
    t_head.next = head
    self.res(head, t_head)
    return t_head.next

def res(self, cur, pre):
    if not cur:
        return
    if cur.val == pre.val:
        self.last.next = cur.next
    elif cur.next and cur.val != cur.next.val:
        self.last = cur
    self.res(cur.next, cur)






def deleteDuplicates(self, head: ListNode) -> ListNode:
    if not head:return head
    if head.next and head.val == head.next.val:
        while head.next != None and head.val == head.next.val:
            head = head.next
        return self.deleteDuplicates(head.next)
    else:
        head.next = self.deleteDuplicates(head.next)
    return head












def deleteDuplicates(self, head):
    dummy = pre = ListNode(0)
    dummy.next = head
    while head and head.next:
        if head.val == head.next.val:
            while head and head.next and head.val == head.next.val:
                head = head.next
            head = head.next
            pre.next = head
        else:
            pre = pre.next
            head = head.next
    return dummy.next


def deleteDuplicates(self, head: ListNode) -> ListNode:
    prev = ans = ListNode(0)        
    prev.next = h = head
    
    while h and h.next:
        remove = False
        while h.next and h.val == h.next.val:
            h.next = h.next.next
            remove = True
        if remove:
            prev.next = h.next
        else:
            prev = prev.next
        h = h.next
    return ans.next



def deleteDuplicates(self, head):
    if not (head and head.next):
        return head
    dummy = ListNode(-1)
    dummy.next = head
    a = dummy
    b = head
    while b and b.next:
        if a.next.val!=b.next.val:
            a = a.next
            b = b.next
        else:
            while b and b.next and a.next.val==b.next.val:
                b = b.next
            a.next = b.next
            b = b.next
    return dummy.next



def deleteDuplicates(self, head):
    if not (head and head.next):
        return head
    dummy = ListNode(-1)
    dummy.next = head
    a = dummy
    b = head.next
    while b:
        if a.next.val!=b.val:
            a = a.next
            b = b.next
        else:
            while b and a.next.val==b.val:
                b = b.next
            # 这里的去重跟解法二有点差别，解法二的是
            # a.next = b.next
            a.next = b
            # b指针在while中判断完后，可能指向了null，这里需要处理边界问题
            b = b.next if b else None
    return dummy.next



def deleteDuplicates(self, head: ListNode) -> ListNode:
    if head == None or head.next == None:
        return head
    dummy = ListNode(-1)
    dummy.next = head
    slow = dummy
    fast = dummy.next
    while fast:
        while fast.next and slow.next.val == fast.next.val:
            fast = fast.next
        # smart
        if slow.next == fast:
            slow = fast
        else:
            slow.next = fast.next
        fast = fast.next
    return dummy.next




def deleteDuplicates(self, head: ListNode) -> ListNode:
    thead = ListNode('a')
    thead.next = head
    pre,cur = None,thead
    while cur:
        pre=cur
        cur=cur.next
        while cur and cur.next and cur.next.val == cur.val:
            t=cur.val
            while cur and cur.val==t:
                cur=cur.next
        pre.next=cur
    return thead.next



def deleteDuplicates(self, head: ListNode) -> ListNode:
    prev = ans = ListNode(0)        
    prev.next = h = head
    
    while h and h.next:
        remove = False
        while h.next and h.val == h.next.val:
            h.next = h.next.next
            remove = True
        if remove:
            prev.next = h.next
        else:
            prev = prev.next
        h = h.next
    return ans.next




def deleteDuplicates(self, head):    
    if head==None:
        return None
    dummy=ListNode(0)
    dummy.next=head
    cur=head
    prev=dummy
    dup=0
    while cur!=None and cur.next!=None:
        if cur.val==cur.next.val:
            cur=cur.next
            dup=1
        else:
            if dup==1:
                prev.next=cur.next
                cur=cur.next
                dup=0
            else:
                prev=cur
                cur=cur.next
    if dup==1:
        prev.next=cur.next
        cur=cur.next
    return dummy.next































def deleteDuplicates(self, head):
        if not (head and head.next):
            return head
        # 用哈希表记录每个节点值的出现频率
        d = dict()
        p = head
        arr = []
        while p:
            val = p.val
            d[val] = d.setdefault(val,0)+1
            p = p.next
        # 将所有只出现一次的值放到arr中，之后再对这个arr排序
        for k in d:
            if d[k]==1:
                arr.append(k)
        arr = sorted(arr)
        dummy = ListNode(-1)
        p = dummy
        # 创建长度为len(arr)长度的链表，依次将arr中的值赋给每个链表节点
        for i in arr:
            tmp = ListNode(i)
            p.next = tmp
            p = p.next
        return dummy.next






















































