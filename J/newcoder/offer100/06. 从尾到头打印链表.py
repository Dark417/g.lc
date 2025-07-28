"""
06. 从尾到头打印链表
输入一个链表的头节点，从尾到头反过来返回每个节点的值（用数组返回）。


示例 1：

输入：head = [1,3,2]
输出：[2,3,1]



"""


# D
def reversePrint(self, head: ListNode) -> List[int]:
    l = []
    while head:
        l.append(head.val)
        head = head.next
    return l[::-1]	# 或者 reverse(res)


def reversePrint(self, head: ListNode) -> List[int]:
    l = []
    while head:
        l.append(head)
        head = head.next
    return [i.val for i in l[::-1]]


def reversePrint(self, head: ListNode) -> List[int]:
    l = []
    res = []
    while head:
        l.append(head.val) #head
        head = head.next
    while l:
        res.append(l.pop())	#.val
    return res


# Krahets
def reversePrint(self, head: ListNode) -> List[int]:
   	return self.reversePrint(head.next) + [head.val] if head else []


def reversePrint(self, head: ListNode) -> List[int]:
    res = []
    while head:
        res = [head.val] + res
        head = head.next
    return res


def reversePrint(self, head: ListNode) -> List[int]:
    if head == None:
        return []

    res = []
    self.helper(head, res)
    return res

def helper(self, node, res):
    if node is None:
        return
    # 应该先判断下一个结点是否为空，如果不为空，则递归调用，在回溯的时候，才添加到结果中
    if node.next:
        self.helper(node.next, res)
    # 回溯时添加
    res.append(node.val)





















