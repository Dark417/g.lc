"""
LinkedList
008 反打印链表

输入一个链表，按链表从尾到头的顺序返回一个ArrayList。




"""


def printListFromTailToHead(self, listNode):
    # write code here
    l = []
    head = listNode
    while head:
        l.insert(0, head.val)
        head = head.next
    return l




