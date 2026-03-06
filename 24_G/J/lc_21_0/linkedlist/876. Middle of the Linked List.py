#!/usr/bin/env python
# coding: utf-8

# In[ ]:


876. Middle of the Linked List
LinkedList, TwoPointer

Given a non-empty, singly linked list with head node head, return a middle node of linked list.

If there are two middle nodes, return the second middle node.

Example 1:

Input: [1,2,3,4,5]
Output: Node 3 from this list (Serialization: [3,4,5])
The returned node has value 3.  (The judge's serialization of this node is [3,4,5]).
Note that we returned a ListNode object ans, such that:
ans.val = 3, ans.next.val = 4, ans.next.next.val = 5, and ans.next.next.next = NULL.

Example 2:

Input: [1,2,3,4,5,6]
Output: Node 4 from this list (Serialization: [4,5,6])
Since the list has two middle nodes with values 3 and 4, we return the second one.


# In[1]:


input1 = [1,2,3,4,5]
input2 = [1,2,3,4,5,6]


# In[13]:


6//2


# In[19]:


def midoflist(input):
#     mid = 0
    mid = input[len(input)//2]
#     if len(input)%2==1:
#         mid = input[len(input)%2 + 1]
#     else:
#         mid = 
    return mid


# In[21]:


output = midoflist(input2)
output


# In[ ]:


def middleNode(self, head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow


# In[ ]:


class Solution:
	def middleNode(self, head: ListNode) -> ListNode:
		current = head      # current node will be used for iteration
		count = 0
		while current:      # as long as there's next node
			count += 1      # count number of nodes
			current = current.next      # and go to the next node

		middle_idx = int(count / 2)     # calculate middle index - int used for rounding it down

		current = head      # let's start from the beginning of the list
		for _ in range(middle_idx):     # with loop with middle_idx steps
			current = current.next      # go further at every step as long as you reach middle node

		return current      # return this node


# In[ ]:


class Solution(object):
    def middleNode(self, head):
        cnt = 0
        mm = head
        while head != None:

            if cnt % 2 == 1:
                mm = mm.next

            head = head.next
            cnt += 1

        return mm


# In[ ]:


class Solution(object):
    def middleNode(self, head):
        """
        :type head: ListNode
        :rtype: ListNode
        """
        curr = head
        count = 0
        while curr is not None:
            count += 1
            curr = curr.next
        
        n = ListNode(-1); n.next = head
        i, curr = 1, n
        while i <= count/2+1:
            curr = curr.next
            i += 1
        return curr


# In[ ]:


class Solution:
    def middleNode(self, head: ListNode) -> ListNode:
        count = 0
        current = head
        #Loop to find the number of nodes
        while current:
            count += 1
            current = current.next
        #Find the target index of middle node
        target = count //2
        count = 0
        current = head
        #Traverse from beginning until our target node and then return it
        while count != target:
            count += 1
            current = current.next
        return current

