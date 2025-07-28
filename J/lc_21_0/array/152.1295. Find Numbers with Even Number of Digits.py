"""
152.1295. Find Numbers with Even Number of Digits
统计位数为偶数的数字

Given an array nums of integers, return how many of them contain an even number of digits.
 

Example 1:

Input: nums = [12,345,2,6,7896]
Output: 2
Explanation: 
12 contains 2 digits (even number of digits). 
345 contains 3 digits (odd number of digits). 
2 contains 1 digit (odd number of digits). 
6 contains 1 digit (odd number of digits). 
7896 contains 4 digits (even number of digits). 
Therefore only 12 and 7896 contain an even number of digits.
Example 2:

Input: nums = [555,901,482,1771]
Output: 1 
Explanation: 
Only 1771 contains an even number of digits.
 

Constraints:

1 <= nums.length <= 500
1 <= nums[i] <= 10^5

"""



return sum(1 for num in nums if int(math.log10(num) + 1) % 2 == 0)


#return sum(1 for i in nums if not i%2)
return sum(1 for num in nums if len(str(num)) % 2 == 0)


return len([x for x in nums if len(str(x)) % 2 == 0])


return sum(len(str(n)) % 2 == 0 for n in nums)
return sum(int(math.log10(n)) % 2 for n in nums) # log10(n) + 1 is the # of digits.


for e in range(30):
	for x in range(10**e-1, 10**e+2):
		if x == 0: continue
		a = len(str(x))
		b = int(log10(x)) + 1
		if a != b:
			print(x, a, b)







































