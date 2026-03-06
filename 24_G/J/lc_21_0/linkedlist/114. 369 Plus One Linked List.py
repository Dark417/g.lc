"""
114. 369 Plus One Linked List 
给单链表加一


用一个 非空 单链表来表示一个非负整数，然后将这个整数加一。

你可以假设这个整数除了 0 本身，没有任何前导的 0。

这个整数的各个数位按照 高位在链表头部、低位在链表尾部 的顺序排列。

示例:

输入: [1,2,3]
输出: [1,2,4]


"""




def plusOne(self, head: ListNode) -> ListNode:
    def recur(node):
        if not node:
            return 1
        car = recur(node.next)
        car += node.val
        node.val = car % 10
        return car // 10
    
    if not head:
        return None
    car = recur(head)
    if car:
        pre = ListNode(1)
        pre.next = head
    return pre if car else head






# official
def plusOne(self, head: ListNode) -> ListNode:
    # sentinel head
    sentinel = ListNode(0)
    sentinel.next = head
    not_nine = sentinel
    
    # find the rightmost not-nine digit
    while head:
        if head.val != 9:
            not_nine = head
        head = head.next 
    
    # increase this rightmost not-nine digit by 1
    not_nine.val += 1
    not_nine = not_nine.next 
    
    # set all the following nines to zeros
    while not_nine:
        not_nine.val = 0
        not_nine = not_nine.next
    
    return sentinel if sentinel.val else sentinel.next



def plusOne(self, head: ListNode) -> ListNode:
    def recursion(node: ListNode):
        # 终止条件: 链表尾部节点, 加1后直接返回
        if not node.next:
            node.val += 1
            return
        # 递归下一个节点
        recursion(node.next)
        # 递归完成后处理当前层节点:判断next节点是否大于0, 如果大于9的话, 减10后进位
        if node.next.val > 9:
            node.next.val -= 10
            if node.val:
                node.val += 1
            else:
                n = ListNode(1)
                n.next, node.next = node.next, n


    sentry = ListNode(None)
    sentry.next = head
    recursion(sentry)
    return sentry.next



def plusOne(self, head):
    setinel = ListNode(0)
    setinel.next = head
    node = setinel
    while node:
        if node.val != 9:
            lastNotNineNode = node
        node = node.next
    lastNotNineNode.val += 1
    node = lastNotNineNode.next
    while node:
        node.val = 0
        node = node.next
    return setinel if setinel.val else setinel.next


def plusOne(self, head):
    setinel = ListNode(0)
    setinel.next = head
    carry = self.helper(head)
    if carry == 1:
        newHead = ListNode(1)
        newHead.next = head
        setinel.next = newHead
    return setinel.next       
def helper(self, node):
    if node.next == None:
        node.val += 1
        if node.val == 10:
            node.val = 0
            carry = 1
        else:
            carry = 0
        return carry
    carry = self.helper(node.next)
    if carry == 1:
        node.val += 1
        if node.val == 10:
            node.val = 0
            carry = 1
        else:
            carry = 0
    return carry


def plusOne(self, head: ListNode) -> ListNode:
    def deep(head):
        if head.next == None:
            head.val += 1
            if head.val == 10:
                head.val = 0
                return True
            else:
                return False
        get = deep(head.next)
        if get:
            head.val += 1
            if head.val == 10:
                head.val = 0
                return True
            else:
                return False
    get = deep(head)
    if get :
        head2 = ListNode(1)
        head2.next = head
        return head2
    else:
        return head


def plusOne(self, head: ListNode) -> ListNode:
    if head:
        num=head.val
        while head.next!=None:
            num=10*num+head.next.val
            head=head.next
    num+=1
    num=str(num)
    self.head=ListNode(num[0])
    p=self.head
    r=self.head
    for i in num[1:]:
        node=ListNode(i)
        p.next=node
        p=p.next
    return r













































