"""
t1.[编程题]万万没想到之聪明的编辑

1. 三个同样的字母连在一起，一定是拼写错误，去掉一个的就好啦：比如 helllo -> hello
2. 两对一样的字母（AABB型）连在一起，一定是拼写错误，去掉第二对的一个字母就好啦：比如 helloo -> hello
3. 上面的规则优先“从左到右”匹配，即如果是AABBCC，虽然AABB和BBCC都是错误拼写，应该优先考虑修复AABB，结果为AABCC


输入描述:
第一行包括一个数字N，表示本次用例包括多少个待校验的字符串。

后面跟随N行，每行为一个待校验的字符串。

输出描述:
N行，每行包括一个被修复后的字符串。

输入例子1:
2
helloo
wooooooow

输出例子1:
hello
woow


"""

def rec(s):
	if len(s) < 3:
		return "".join(s)
	if len(s) >= 3:
		if s[0] == s[1] == s[2]:
			return "".join(s[0:2]) + rec(s[3:])
	if len(s) >=4:
		if s[0] == s[1] and s[2] == s[3]:
			return "".join(s[0:3]) + rec(s[4:])




n = int(input())
for _ in range(n):
	l = list(input())
	s = ""
	print(rec(l))





n = int(input())
for _ in range(n):
	l = list(input())
	s = ""
	for i in range(len(l)):
		if len(l) - i >= 3:
			if l[i] == l[i+1] == l[i+2]:
				l.pop(l[i+2])
		elif len(l) - i >= 4:
			if l[i] == l[i+1] and l[i+2] == l[i+3]:
				l.pop(l[i+3])
	print("".join(l))




"""
t2. [编程题]万万没想到之抓捕孔连顺

请听题：给定N（可选作为埋伏点的建筑物数）、D（相距最远的两名特工间的距离的最大值）以及可选建筑的坐标，计算在这次行动中，大锤的小队有多少种埋伏选择。
注意：
1. 两个特工不能埋伏在同一地点
2. 三个特工是等价的：即同样的位置组合(A, B, C) 只算一种埋伏方法，不能因“特工之间互换位置”而重复使用

输入描述:
第一行包含空格分隔的两个数字 N和D(1 ≤ N ≤ 1000000; 1 ≤ D ≤ 1000000)

第二行包含N个建筑物的的位置，每个位置用一个整数（取值区间为[0, 1000000]）表示，从小到大排列（将字节跳动大街看做一条数轴）

输出描述:
一个数字，表示不同埋伏方案的数量。结果可能溢出，请对 99997867 取模

输入例子1:
4 3
1 2 3 4

输出例子1:
4

例子说明1:
可选方案 (1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4)

输入例子2:
5 19
1 10 20 30 50

输出例子2:
1

例子说明2:
可选方案 (1, 10, 20)
"""



n, d = map(int, input().split())
nums = list(map(int, input().split()))


res = 0
left = 0
right = 2

while left < n-2:
	print(left, right)
	while right < n and nums[right] - nums[left] <= dist:
        right += 1
    if right - 1 - left >= 2:
        num = right - left - 1
        res += num * (num - 1) // 2
    left += 1

print(res % 99997867)










































































































































