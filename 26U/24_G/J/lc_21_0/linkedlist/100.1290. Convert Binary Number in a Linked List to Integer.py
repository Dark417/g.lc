"""
100.1290. Convert Binary Number in a Linked List to Integer
二进制链表转整数


Given head which is a reference node to a singly-linked list. The value of each node in
the linked list is either 0 or 1. The linked list holds the binary representation of a number.

Return the decimal value of the number in the linked list.

 

Example 1:


Input: head = [1,0,1]
Output: 5
Explanation: (101) in base 2 = (5) in base 10
Example 2:

Input: head = [0]
Output: 0
Example 3:

Input: head = [1]
Output: 1
Example 4:

Input: head = [1,0,0,1,0,0,1,1,1,0,0,0,0,0,0]
Output: 18880
Example 5:

Input: head = [0,0]
Output: 0
 

Constraints:

The Linked List is not empty.
Number of nodes will not exceed 30.
Each node's value is either 0 or 1.



"""





# official
def getDecimalValue(self, head: ListNode) -> int:
    cur = head
    ans = 0
    while cur:
        ans = ans * 2 + cur.val
        cur = cur.next
    return ans


"""
这样就失去指向第一个节点的head“指针”了 最好别破坏原始结构和“指针”
def getDecimalValue(self, head: ListNode) -> int:
    ans = 0
    while head:
        ans = ans * 2 + head.val
        head = head.next
    return ans

"""

def getDecimalValue(self, head: ListNode) -> int:
    l = "0b"
    while head:
        l+=str(head.val)
        head = head.next
    res = int(l,2)
    return res


def getDecimalValue(self, head: ListNode) -> int:
    re = 0
    tmp = head
    while tmp is not None:
        re = (re << 1) | tmp.val
        tmp = tmp.next
    return re


def getDecimalValue(self, head: ListNode) -> int:
    answer = 0
    while head: 
        answer = 2*answer + head.val 
        head = head.next 
    return answer 



def getDecimalValue(self, head):
    rst = 0
    while head:
        rst <<= 1
        rst |= head.val
        head = head.next
    return rst



def getDecimalValue(self, head: ListNode) -> int:
    binaryNumberString = ""
    while head:
        binaryNumberString += str(head.val)
        head = head.next
    return int(binaryNumberString,2)


def getDecimalValue(self, head):
    bins = []
    while head:
        bins.append(str(head.val))
        head = head.next
    return int(''.join(bins),2)



def getDecimalValue(self, head):
    return self.get_value(head, 0)

    def get_value(self, head, s):
        if head.next is not None:
            return self.get_value(head.next, 2 * s + head.val)
        return 2 * s + head.val



def getDecimalValue(self, head: ListNode) -> int:
    cur = head
    ans = count = 0
    stack = []
    while cur:
        stack.append(cur.val)
        cur = cur.next
    while stack:
        top = stack.pop()
        if top == 1:
            ans = ans + pow(2, count)   
        count += 1 
    return ans





























