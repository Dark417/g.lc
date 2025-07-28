"""
122. Best Time to Buy and Sell Stock II
买卖股票的最佳时机 II

Say you have an array prices for which the ith element is the price of a given stock on day i.

Design an algorithm to find the maximum profit. You may complete as many 
transactions as you like (i.e., buy one and sell one share of the stock multiple times).

Note: You may not engage in multiple transactions at the same time (i.e., 
you must sell the stock before you buy again).

Example 1:

Input: [7,1,5,3,6,4]
Output: 7
Explanation: Buy on day 2 (price = 1) and sell on day 3 (price = 5), profit = 5-1 = 4.
             Then buy on day 4 (price = 3) and sell on day 5 (price = 6), profit = 6-3 = 3.
Example 2:

Input: [1,2,3,4,5]
Output: 4
Explanation: Buy on day 1 (price = 1) and sell on day 5 (price = 5), profit = 5-1 = 4.
             Note that you cannot buy on day 1, buy on day 2 and sell them later, as you are
             engaging multiple transactions at the same time. You must sell before buying again.
Example 3:

Input: [7,6,4,3,1]
Output: 0
Explanation: In this case, no transaction is done, i.e. max profit = 0.
 

Constraints:

1 <= prices.length <= 3 * 10 ^ 4
0 <= prices[i] <= 10 ^ 4

"""

nums1[:] = sorted(nums1[:m] + nums2)

def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
    nums1[m:] = nums2
    nums1.sort()



def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
    i = j = 0
    l = []
    #num1 = nums1[:m]
    while i < m and j < n:
        if nums1[i] <= nums2[j]:
            l.append(nums1[i])
            i += 1
        else:
            l.append(nums2[j])
            j += 1
    while i < m:
        l.append(nums1[i])
        i += 1
    while j < n:
        l.append(nums2[j])
        j += 1
    nums1[:] = l



def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
    i = j = 0
    l = []
    num1 = nums1[:m]
    while i < m and j < n:
        if nums1[i] <= nums2[j]:
            l.append(nums1[i])
            i += 1
        else:
            l.append(nums2[j])
            j += 1
    if i < m:
        l += nums1[i:m]
    if j < n:
        l += nums2[j:]
    nums1[:] = l





def merge(self, nums1, m, nums2, n):
    # Make a copy of nums1.
    nums1_copy = nums1[:m] 
    nums1[:] = []

    # Two get pointers for nums1_copy and nums2.
    p1 = 0 
    p2 = 0
    
    # Compare elements from nums1_copy and nums2
    # and add the smallest one into nums1.
    while p1 < m and p2 < n: 
        if nums1_copy[p1] < nums2[p2]: 
            nums1.append(nums1_copy[p1])
            p1 += 1
        else:
            nums1.append(nums2[p2])
            p2 += 1

    # if there are still elements to add
    if p1 < m: 
        nums1[p1 + p2:] = nums1_copy[p1:]
    if p2 < n:
        nums1[p1 + p2:] = nums2[p2:]



def merge(self, nums1, m, nums2, n):
    # two get pointers for nums1 and nums2
    p1 = m - 1
    p2 = n - 1
    # set pointer for nums1
    p = m + n - 1

    # while there are still elements to compare
    while p1 >= 0 and p2 >= 0:
        if nums1[p1] < nums2[p2]:
            nums1[p] = nums2[p2]
            p2 -= 1
        else:
            nums1[p] =  nums1[p1]
            p1 -= 1
        p -= 1

    # add missing elements from nums2
    nums1[:p2 + 1] = nums2[:p2 + 1]



def merge(self, nums1, m, nums2, n):
    while m > 0 and n > 0:
        if nums1[m-1] >= nums2[n-1]:
            nums1[m+n-1] = nums1[m-1]
            m -= 1
        else:
            nums1[m+n-1] = nums2[n-1]
            n -= 1
    if n > 0:
        nums1[:n] = nums2[:n]



# caikehe
def merge(self, nums1, m, nums2, n):
    l1, l2, end = m-1, n-1, m+n-1
    while l1 >= 0 and l2 >= 0:
        if nums2[l2] > nums1[l1]:
            nums1[end] = nums2[l2]
            l2 -= 1
        else:
            nums1[end] = nums1[l1]
            l1 -= 1
        end -= 1
    if l1 < 0: # if nums2 left
        nums1[:l2+1] = nums2[:l2+1]

def merge1(self, nums1, m, nums2, n):
	m, n = m-1, n-1
	while m >= 0 and n >= 0:
	    if nums1[m] > nums2[n]:
	        nums1[m+n+1] = nums1[m]
	        m -= 1
	    else:
	        nums1[m+n+1] = nums2[n]
	        n -= 1
	if n != -1: # nums2 is still left
	    nums1[:n+1] = nums2[:n+1]




































































