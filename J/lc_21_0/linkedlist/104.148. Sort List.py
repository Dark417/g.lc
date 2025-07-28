"""
104.148. Sort List
排序链表


Sort a linked list in O(n log n) time using constant space complexity.

Example 1:

Input: 4->2->1->3
Output: 1->2->3->4
Example 2:

Input: -1->5->3->4->0
Output: -1->0->3->4->5


"""


# D
def sortList(self, head: ListNode) -> ListNode:
    if not head: return None
    if not head.next: return head

    l1 = l2 = head
    while l2.next and l2.next.next:
        l1 = l1.next
        l2 = l2.next.next
    l2 = l1.next
    l1.next = None

    head = self.sortList(head)
    b = self.sortList(l2)
    return self.merge2lists(head, b)

def merge2lists(self, l1, l2):
    if l1 and l2:
        if l1.val > l2.val:
            l1, l2 = l2, l1
        l1.next = self.merge2lists(l1.next, l2)
    return l1 or l2





# Krahets
def sortList(self, head: ListNode) -> ListNode:
    if not head or not head.next: return head # termination.
    # cut the LinkedList at the mid index.
    slow, fast = head, head.next
    while fast and fast.next:
        fast, slow = fast.next.next, slow.next
    mid, slow.next = slow.next, None # save and cut.
    # recursive for cutting.
    left, right = self.sortList(head), self.sortList(mid)
    # merge `left` and `right` linked list and return it.
    h = res = ListNode(0)
    while left and right:
        if left.val < right.val: h.next, left = left, left.next
        else: h.next, right = right, right.next
        h = h.next
    h.next = left if left else right
    return res.next



def sortList(self, head: ListNode) -> ListNode:
    h, length, intv = head, 0, 1
    while h: h, length = h.next, length + 1
    res = ListNode(0)
    res.next = head
    # merge the list in different intv.
    while intv < length:
        pre, h = res, res.next
        while h:
            # get the two merge head `h1`, `h2`
            h1, i = h, intv
            while i and h: h, i = h.next, i - 1
            if i: break # no need to merge because the `h2` is None.
            h2, i = h, intv
            while i and h: h, i = h.next, i - 1
            c1, c2 = intv, intv - i # the `c2`: length of `h2` can be small than the `intv`.
            # merge the `h1` and `h2`.
            while c1 and c2:
                if h1.val < h2.val: pre.next, h1, c1 = h1, h1.next, c1 - 1
                else: pre.next, h2, c2 = h2, h2.next, c2 - 1
                pre = pre.next
            pre.next = h1 if c1 else h2
            while c1 > 0 or c2 > 0: pre, c1, c2 = pre.next, c1 - 1, c2 - 1
            pre.next = h 
        intv *= 2
    return res.next



# quicksort
def sortList(self, head: ListNode) -> ListNode:
    if head is None:
        return head

    # 分成三个链表，分别是比轴心数小，相等，大的数组成的链表
    big = None
    small = None
    equal = None
    cur = head
    while cur is not None:
        t = cur
        cur = cur.next
        if t.val < head.val:
            t.next = small
            small = t
        elif t.val > head.val:
            t.next = big
            big = t
        else:
            t.next = equal
            equal = t
    
    # 拆完各自排序即可，equal 无需排序
    big = self.sortList(big)
    small = self.sortList(small)

    ret = ListNode(None)
    cur = ret

    # 将三个链表组合成一起，这一步复杂度是 o(n)
    # 可以同时返回链表的头指针和尾指针加速链表的合并。
    for p in [small, equal, big]:
        while p is not None:
            cur.next = p
            p = p.next
            cur = cur.next
            cur.next = None
    return ret.next




















# caikehe
# merge sort, recursively 
def sortList(self, head):
    if not head or not head.next:
        return head
    # divide list into two parts
    fast, slow = head.next, head
    while fast and fast.next:
        fast = fast.next.next
        slow = slow.next
    second = slow.next
    # cut down the first part
    slow.next = None
    l = self.sortList(head)
    r = self.sortList(second)
    return self.merge(l, r)
    
# merge in-place without dummy node        
def merge(self, l, r):
    if not l or not r:
        return l or r
    if l.val > r.val:
        l, r = r, l
    # get the return node "head"
    head = pre = l
    l = l.next
    while l and r:
        if l.val < r.val:
            l = l.next
        else:
            nxt = pre.next
            pre.next = r
            tmp = r.next
            r.next = nxt
            r = tmp
        pre = pre.next
    # l and r at least one is None
    pre.next = l or r
    return head

def merge(self, l, r):
    if not l or not r:
        return l or r
    if l.val > r.val:
        l, r = r, l
    # get the return node "head"
    head = pre = l
    l = l.next
    while l and r:
        if l.val < r.val:
            pre.next = l
            l = l.next
        else:
            pre.next = r
            r = r.next
        pre = pre.next
    # l and r at least one is None
    pre.next = l or r
    return head


# wong
def sortList(self, head):
    if head is None or head.next is None:
        return head
    middle_node = self.find_middle_node(head)
    right_head = middle_node.next
    middle_node.next = None
    return self.merge(self.sortList(head), self.sortList(right_head))

def find_middle_node(self, head):
    slow, fast = head, head
    while fast and fast.next and fast.next.next:
        fast = fast.next.next
        slow = slow.next
    return slow
    
def merge(self, head1, head2):
    dummy = ListNode(None)
    node = dummy
    while head1 and head2:
        if head1.val < head2.val:
            node.next = head1
            head1 = head1.next
        else:
            node.next = head2
            head2 = head2.next
        node = node.next
        
    node.next = head1 or head2
    return dummy.next




# clean
def merge(self, h1, h2):
    dummy = tail = ListNode(None)
    while h1 and h2:
        if h1.val < h2.val:
            tail.next, tail, h1 = h1, h1, h1.next
        else:
            tail.next, tail, h2 = h2, h2, h2.next

    tail.next = h1 or h2
    return dummy.next

def sortList(self, head):
    if not head or not head.next:
        return head

    pre, slow, fast = None, head, head
    while fast and fast.next:
        pre, slow, fast = slow, slow.next, fast.next.next
    pre.next = None

    return self.merge(*map(self.sortList, (head, slow)))






# merge sort
def sortList(self, head: ListNode) -> ListNode:
        if not head or not head.next:
            return head 

        res = self.split_merge(head)

        return res 

    def split_merge(self, left_start):
        if not left_start or not left_start.next:
            return left_start 

        # find mid node then split this ListNode into two piece 
        fast, slow = left_start, left_start 
        while fast.next and fast.next.next:
            fast = fast.next.next 
            slow = slow.next 

        # right_start = slow.next # 这里是右边的开始节点
        right = self.split_merge(slow.next)
        slow.next = None 
        left = self.split_merge(left_start) # 这里还是用了递归，有栈的额外空间损耗。怎么减少呢？
        

        return self.merge(left, right)

    def merge(self, left, right):
        if not left:
            return right 
        if not right:
            return left 
        res = dummy_node = ListNode(0)
        while left and right:
            if left.val < right.val:
                dummy_node.next = left 
                dummy_node = dummy_node.next 
                left = left.next 
            else:
                dummy_node.next = right 
                dummy_node = dummy_node.next 
                right = right.next 
        if left:
            dummy_node.next = left 
        if right:
            dummy_node.next = right  
        return res.next


def sortList(self, head: ListNode) -> ListNode:
    # 特判
    if not head or not head.next:
        return head 
    
    # 找到长度
    length_h = head 
    length = 0 
    while length_h:
        length_h = length_h.next 
        length += 1 
    
    # 合并
    unit_length = 1
    res = ListNode(0)
    res.next = head
    # 针对不同的单元长度，我们要分别进行merge。从单元长度为1 开始 接着为2 为4 ****
    while unit_length < length:
        pre, start_node = res, res.next
        
        while start_node:
            # 只要当前节点还没有走到最后，那么就一直进行 两两合并的操作，
            unit_odd, unit_odd_length = start_node, 0
            while start_node and unit_odd_length < unit_length:
                # 要找到我们想要的奇数节点的那一段
                start_node = start_node.next
                unit_odd_length += 1 
            if unit_odd_length < unit_length:
                # 说明此时节点已经到头了，但是单元长度依然大于我们希望的单元长度，
                # 则说明链表长度不够，后面没有了，可以直接break
                break 

            unit_even, unit_even_length = start_node, 0 
            while start_node and unit_even_length < unit_length:
                start_node = start_node.next
                unit_even_length += 1 
            
            # 利用长度来限制合并到哪些节点
            while unit_odd_length and unit_even_length:
                if unit_odd.val < unit_even.val:
                    pre.next = unit_odd
                    unit_odd = unit_odd.next 
                    pre = pre.next
                    unit_odd_length -= 1 
                else:
                    pre.next = unit_even
                    unit_even = unit_even.next 
                    pre = pre.next
                    unit_even_length -= 1 
                
            pre.next = unit_odd if unit_odd_length > 0 else unit_even

            while unit_odd_length > 0 or unit_even_length > 0:
                pre = pre.next
                unit_odd_length -= 1
                unit_even_length -= 1
            pre.next = start_node
            
        unit_length *= 2

    return res.next














def sortList(self, head):
        """
        :type head: ListNode
        :rtype: ListNode
        """
        if not head or not head.next: return head
        dummy = ListNode('s'); dummy.next = head; tmp = head
        length = 0
        while tmp:
            tmp = tmp.next
            length += 1
        step = 1
        while step<length:
            cur, tail = dummy.next, dummy
            while cur:
                left = cur
                right = self.split(left,step)
                cur = self.split(right, step)
                tail = self.merge2(left,right,tail)
            step <<= 1
        return dummy.next
    
    # merge 2 sorted lists, and append the result to head
    # return the tail
    def merge2(self, p1, p2, head):
        dummy = ListNode('#');p = dummy
        while p1 and p2:
            if p1.val <= p2.val:
                p.next = p1
                p1 = p1.next; p = p.next
            else:
                p.next = p2
                p2 = p2.next; p = p.next
        p.next = p1 or p2
        head.next = dummy.next
        while p.next: p = p.next
        return p

    # divide the linked list into two lists
    # first linked list contains n nodes
    # return the head of second linked list
    def split(self, head, n):
        for i in range(n-1): 
            if head: head = head.next
            else: break
        if not head: return None
        second = head.next
        head.next = None
        return second





def sortList(self, head):
    def partition(start, end):
        node = start.next.next
        pivotPrev = start.next
        pivotPrev.next = end
        pivotPost = pivotPrev
        while node != end:
            temp = node.next
            if node.val > pivotPrev.val:
                node.next = pivotPost.next
                pivotPost.next = node
            elif node.val < pivotPrev.val:
                node.next = start.next
                start.next = node
            else:
                node.next = pivotPost.next
                pivotPost.next = node
                pivotPost = pivotPost.next
            node = temp
        return [pivotPrev, pivotPost]
    
    def quicksort(start, end):
        if start.next != end:
            prev, post = partition(start, end)
            quicksort(start, prev)
            quicksort(post, end)

    newHead = ListNode(0)
    newHead.next = head
    quicksort(newHead, None)
    return newHead.next











