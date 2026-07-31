# 138.109. 有序链表转换二叉搜索树

def sortedListToBST(self, head: ListNode) -> TreeNode:
    def getMedian(left: ListNode, right: ListNode) -> ListNode:
        fast = slow = left
        while fast != right and fast.next != right:
            fast = fast.next.next
            slow = slow.next
        return slow
    
    def buildTree(left: ListNode, right: ListNode) -> TreeNode:
        if left == right:
            return None
        mid = getMedian(left, right)
        root = TreeNode(mid.val)
        root.left = buildTree(left, mid)
        root.right = buildTree(mid.next, right)
        return root
    
    return buildTree(head, None)



def sortedListToBST(self, head: ListNode) -> TreeNode:
    def getLength(head: ListNode) -> int:
        ret = 0
        while head:
            ret += 1
            head = head.next
        return ret
    
    def buildTree(left: int, right: int) -> TreeNode:
        if left > right:
            return None
        mid = (left + right + 1) // 2
        root = TreeNode()
        root.left = buildTree(left, mid - 1)
        nonlocal head
        root.val = head.val
        head = head.next
        root.right = buildTree(mid + 1, right)
        return root
    
    length = getLength(head)
    return buildTree(0, length - 1)











































