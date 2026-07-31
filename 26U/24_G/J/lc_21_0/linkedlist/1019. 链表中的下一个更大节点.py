# 1019. 链表中的下一个更大节点


def nextLargerNodes(self, head):
    res, stack = [], []
    while head:
        while stack and stack[-1][1] < head.val:
            res[stack.pop()[0]] = head.val
        stack.append([len(res), head.val])
        res.append(0)
        head = head.next
    return res


        
def nextLargerNodes(self, head: ListNode) -> List[int]:
    lists, stack = [], []
    while head:
        lists.append(head.val)
        head = head.next 
    ans = [0]*len(lists)
    for i in range(len(lists)):
        while stack and lists[stack[-1]] < lists[i]:
            j = stack.pop()
            ans[j] = lists[i]
        stack.append(i)
    return ans


def nextLargerNodes(self, head: ListNode) -> List[int]:        
    stack = []
    stack_loc = []
    loc = -1
    res = []
    while head:
        loc += 1
        res.append(0)
        while stack and stack[-1] < head.val:
            res[stack_loc[-1]] = head.val
            stack.pop()
            stack_loc.pop()
        stack.append(head.val)
        stack_loc.append(loc)  
        head = head.next
    return res



def nextLargerNodes(self, head: ListNode) -> List[int]:
    cur = head
    nums = []
    while cur:
        nums.append(cur.val)
        cur = cur.next
    
    stack = []
    result = [0 for i in range(len(nums))]
    for j in range(len(result)-1, -1, -1):
        if not stack:
            stack.append(nums[j])
            continue
        else:
            x  = nums[j]
            while stack and stack[-1] <= x:
                stack.pop()
            if stack:
               result[j] = stack[-1]
            stack.append(x)
    
    return resul



def nextLargerNodes(self, head: ListNode) -> List[int]:        
    nums = []
    node = head
    while node != None :
        nums.append(node.val)
        node = node.next

    stack = []
    stack_loc = []
    res = [0] * len(nums)

    for i in range(len(nums)):
        while stack and stack[-1] < nums[i]:
            res[stack_loc[-1]] = nums[i]
            stack.pop()
            stack_loc.pop()
        stack.append(nums[i])
        stack_loc.append(i)

    return res                           









def nextLargerNodes(self, head: ListNode) -> List[int]:
    cur = head
    nums = []
    while cur:
        nums.append(cur.val)
        cur = cur.next
    result = []
    a, b = 0, 0
    while b < len(nums):
        if nums[b] > nums[a]:
            result.append(nums[b])
            a += 1
            b = a
        else:
            b += 1
        if b == len(nums):
            result.append(0)
            a += 1
            b = a
    return result


