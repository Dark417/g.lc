"""
110.83. Remove Duplicates from Sorted List
面试题 02.01. 移除重复节点



编写代码，移除未排序链表中的重复节点。保留最开始出现的节点。

示例1:

 输入：[1, 2, 3, 3, 2, 1]
 输出：[1, 2, 3]
示例2:

 输入：[1, 1, 1, 1, 2]
 输出：[1, 2]
提示：

链表长度在[0, 20000]范围内。
链表元素在[0, 20000]范围内。
进阶：

如果不得使用临时缓冲区，该怎么解决？

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/remove-duplicate-node-lcci
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。






"""

def deleteDuplicates(self, head):
    if head and head.next:
        head.next = self.deleteDuplicates(head.next)
        return head.next if head.next.val == head.val else head
    return head





def deleteDuplicates(self, H: ListNode) -> ListNode:
    if H == None: return None
    S = C = ListNode(H.val)
    while H.next != None:
        if H.val != H.next.val:
            C.next = ListNode(H.next.val)
            C = C.next
        H = H.next
    return S


def removeDuplicateNodes(self, head: ListNode) -> ListNode:
    vset = set()
    def rec(node):
        if not node: return node
        if node.val not in vset:
            vset.add(node.val)
            node.next = rec(node.next)
        else:
            node = rec(node.next)
        return node
    return rec(head)


def deleteDuplicates(self, head: ListNode) -> ListNode:
    if not head or not head.next:
        return head
    # remove one node and don't move the head pointer yet 
    if head.val == head.next.val:
        head.next = head.next.next
        self.deleteDuplicates(head)
    else: # not a duplicate search from next node
        head.next = self.deleteDuplicates(head.next)
    return head


    if not head or not head.next:
        return head
    if head.val == head.next.val:
        return self.deleteDuplicates(head.next)
    else: 
        head.next = self.deleteDuplicates(head.next)
        return head



def deleteDuplicates(self, head):
    cur = head
    while cur:
        while cur.next and cur.next.val == cur.val:
            cur.next = cur.next.next     # skip duplicated node
        cur = cur.next     # not duplicate of current node, move to next node
    return head


def deleteDuplicates(self, head: ListNode) -> ListNode:
    prev = None
    curr = head
    while curr:
        prev = curr
        curr = curr.next
        while curr and prev.val == curr.val:
            curr = curr.next
        prev.next = curr
    return head




def deleteDuplicates(self, head):
    if head is None:
        return head
    curr = head
    while curr.next:
        if curr.next.val == curr.val:
            curr.next = curr.next.next
        else:
            curr = curr.next
    return head


def deleteDuplicates1(self, head):
    node = head
    while node and node.next:
        if node.val == node.next.val:
            node.next = node.next.next
        else:
            node = node.next
    return head


def deleteDuplicates(self, head: ListNode) -> ListNode:
    k = set()
    s = p = ListNode(0)
    p.next = head
    while head:
        if head.val not in k:
            k.add(head.val)
            p = p.next
        else:
            p.next = head.next
        head = head.next
    return s.next



def deleteDuplicates(self, head):
    dic = {}
    node = head
    while node:
        dic[node.val] = dic.get(node.val, 0) + 1
        node = node.next
    node = head
    while node:
        tmp = node
        for _ in xrange(dic[node.val]):
            tmp = tmp.next
        node.next = tmp
        node = node.next
    return head


def removeDuplicateNodes(self, head: ListNode) -> ListNode:
    if not head:#如果head里本来就没东西，那就返回head本身
        return head
    r = head #r是head的代言人，负责迭代和更新，head负责原地不动
    record = {head.val} #record负责储存看见过的值。现在已经储存了第一个值

    while r and r.next: #只要r接下来还有东西，就看看下一个东西是不是已经在record当中 
        #这里判断时要同时符合这两个条件，因为如果r已经是None了，判断r.next会报错，所以每次得先判断r
        if r.next.val not in record: #如果下一环的值没被储存过,不用对head作任何修改
            record.add(r.next.val) #在record中添加这个值
            r = r.next #并且让r进入下一环
        else: #如果下一环的值已经见过了
            r.next = r.next.next #直接让r的下一环变为下下环，即把r.next这一环删了
            #这里不用再写"r=r.next"让r进入下一环，原因是r.next已经更改了，要重新进入loop判断现在的r.next(即原来的r.next.next)是否已经遇见过
    return head


def removeDuplicateNodes(self, head: ListNode) -> ListNode:
    val_set=set()
    prev=ListNode(-1)
    prev.next=head

    while prev.next:
        if prev.next.val in val_set:
            prev.next=prev.next.next
        else:
            val_set.add(prev.next.val)
            prev=prev.next
    return head


# deal with next next
# def removeDuplicateNodes(self, head: ListNode) -> ListNode:
#     vset = set()
#     cur = head
#     while cur:
#         if cur.val not in vset:
#             vset.add(cur.val)
#         else:
#             cur = cur.next
#         cur = cur.next
#     return head



"""
public ListNode removeDuplicateNodes(ListNode head) {
        ListNode ob = head;
        while (ob != null) {
            ListNode oc = ob;
            while (oc.next != null) {
                if (oc.next.val == ob.val) {
                    oc.next = oc.next.next;
                } else {
                    oc = oc.next;
                }
            }
            ob = ob.next;
        }
        return head;
    }

"""

# recursion
"""
public ListNode removeDuplicateNodes(ListNode head) {
        return removeDuplicateNodesHelper(head, new HashSet<>());
    }

    public ListNode removeDuplicateNodesHelper(ListNode head, Set<Integer> set) {
        if (head == null)
            return null;
        if (set.contains(head.val))
            return removeDuplicateNodesHelper(head.next, set);
        set.add(head.val);
        head.next = removeDuplicateNodesHelper(head.next, set);
        return head;
    }

"""








def removeDuplicateNodes(self, head: ListNode) -> ListNode:
    if not head: return None
    i = head
    while i:
        pre = i
        cur = i.next
        while cur:
            if cur.val == i.val:
                pre.next = cur.next
            else:
                pre = pre.next
            cur = cur.next
        i = i.next
    return head
















































