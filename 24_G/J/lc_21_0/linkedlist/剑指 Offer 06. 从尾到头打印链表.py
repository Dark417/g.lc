# 剑指 Offer 06. 从尾到头打印链表

def reversePrint(self, head: ListNode) -> List[int]:
    return self.reversePrint(head.next) + [head.val] if head else []




