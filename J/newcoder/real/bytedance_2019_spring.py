"""
2020.4.27
bytedance programming questions
https://www.nowcoder.com/test/question/done?tid=33050607&qid=362290

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

# reduce
# def process(s):
#     for i in range(len(s) - 3):
#
#         if s[i] == s[i + 1] and s[i + 2] == s[i + 3]:
#             s.replace(s[i + 3], "")
#         elif s[i] == s[i + 1] and s[i] == s[i + 2]:
#             s.replace(s[i + 2], "")
#     return s
#
#
# n = int(input())
# strings = [None] * n
#
# for i in range(n):
#     # strings[i] = input()
#     string = input()
#     print(process(string))

# cpy
# n = int(input())
# for i in range(n):
#     line = input()
#     res = ""
#     # res = []
#     for e in line:
#
#         if len(res) < 2:
#             res += e
#             continue
#         if len(res) >= 2:
#             if e == res[-1] and e == res[-2]:
#                 continue
#         if len(res) >= 3:
#             if e == res[-1] and res[-2] == res[-3]:
#                 continue
#         res += e
#     print(res)


# dis
# 链接：https://www.nowcoder.com/questionTerminal/42852fd7045c442192fa89404ab42e92
# 来源：牛客网
#
# n = int(input())
# while n > 0:
#     s = input()
#     res = []
#     for e in s:
#         if len(res) < 2:
#             res.append(e)
#             continue
#         if len(res) >= 2:
#             if e == res[-1] and e == res[-2]:
#                 continue
#         if len(res) >= 3:
#             if e == res[-1] and res[-2] == res[-3]:
#                 continue
#         res.append(e)
#     print("".join(res))
#     n -= 1

#
#
# 链接：https://www.nowcoder.com/questionTerminal/42852fd7045c442192fa89404ab42e92
# 来源：牛客网
#
# def main():
#     n = input()
#     if n == 0&nbs***bsp;n == None:
#         return None
#     for i in range(int(n)):
#         s=input()
#         j=1
#         while(j<=len(s)-1):
#             if j > 2:
#                 if (s[j]==s[j-1]==s[j-2]&nbs***bsp;(s[j]==s[j-1] and s[j-2]==s[j-3])):
#                     s=s[:j]+s[j+1:]
#                 else:
#                     j = j + 1
#             elif (j > 1 and s[j]==s[j-1]==s[j-2]):
#                     s=s[:j]+s[j+1:]
#             else:
#                 j = j + 1
#         print(s)
# if __name__ == '__main__':
#     main()

# 链接：https: // www.nowcoder.com / questionTerminal / 42852
# fd7045c442192fa89404ab42e92
# 来源：牛客网

# import re
#
# def test(ma):
#     return ma.group()[1:]
#
# def test2(ma):
#     return ma.group()[0:len(ma.group()) - 1]
#
# for i in range(int(input())):
#     a = input()
#
#     while re.search(r"(.)\1\1", a):
#         a = re.sub(r"(.)\1\1", test, a)
#
#     while re.search(r"(.)\1(.)\2", a):
#         a = re.sub(r"(.)\1(.)\2", test2, a)
#
#     print(a)

# 链接：https://www.nowcoder.com/questionTerminal/42852fd7045c442192fa89404ab42e92
# 来源：牛客网
#
# import re
# def repair(s):
#     # (.)\1 -> \1表示.匹配到的第一个字符
#     res = re.sub(r'(.)\1\1+', repl=lambda x: x.groups(0)[0]*2, string=s) # 消除三个以上连续
#     res = re.sub(r'(.)\1(.)\2', repl=lambda x: x.groups(0)[0]*2+x.groups(0)[1], string=res)
#     return res
#
# 链接：https://www.nowcoder.com/questionTerminal/42852fd7045c442192fa89404ab42e92
# 来源：牛客网
#
# for i in range(int(input())):
#     b,j = input() + ' ',2
#     while j < len(b) - 1 :
#         if b[j - 2] == b[j - 1]:
#             if b[j] in [b[j - 1],b[j + 1]]:
#                 b,j = b[:j] + b[j + 1:],j - 1
#         j += 1
#     print(b[:-1])






"""
给定N（可选作为埋伏点的建筑物数）、
D（相距最远的两名特工间的距离的最大值）
以及可选建筑的坐标，
计算在这次行动中，大锤的小队有多少种埋伏选择。
输入描述:
第一行包含空格分隔的两个数字 N和D(1 ≤ N ≤ 1000000; 1 ≤ D ≤ 1000000)

第二行包含N个建筑物的的位置，每个位置用一个整数（取值区间为[0, 1000000]）表示，
从小到大排列（将字节跳动大街看做一条数轴）

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

# d
dis = int(input().split()[1])
loc = list(map(int, input().split()))
res = 0

if len(loc) < 3:
    print(0)

for i in range(0, len(loc) - 2):
    # if loc[i] + 2*dis > loc[-1]:
    #     continue

    for j in range(i + 1, len(loc) - 1):
        # if loc[j] + dis > loc[-1]:
        #     continue
        if loc[j] - loc[i] > dis:
            continue

        for k in range(j + 1, len(loc)):
            if loc[k] - loc[i] > dis:
                continue
            res += 1

print(res % 99997867)

# dis
# 链接：https: // www.nowcoder.com / questionTerminal / c0803540c94848baac03096745b55b9b
# 来源：牛客网

# n, dist = map(int, input().split())
# nums = list(map(int, input().split()))
#
# res = 0
# left = 0
# right = 2
#
# while left < n - 2:
#     while right < n and nums[right] - nums[left] <= dist:
#         right += 1
#     if right - 1 - left >= 2:
#         num = right - left - 1
#         res += num * (num - 1) // 2
#     left += 1
#
# print(res % 99997867)

# 链接：https://www.nowcoder.com/questionTerminal/c0803540c94848baac03096745b55b9b
# 来源：牛客网
#
# import itertools
# In = list(map(int,input().split(' ')))
# N = In[0]     #建筑物个数
# D = In[1]     #最大距离
# loc = list(map(int,input().split(' ')))
# result = []
# for i in itertools.combinations(loc,3):
#     result.append(i)
# for i in result[:]:
#     if max(i) - min(i) >D:
#         result.remove(i)
# print(len(result))

# 链接：https://www.nowcoder.com/questionTerminal/c0803540c94848baac03096745b55b9b
# 来源：牛客网
#
# n,d = list(map(eval, input().split()))
# local = list(map(eval, input().split()))
# from itertools import combinations
# may = list(combinations(local,3))
# def filt(it):
#     if abs(it[0] - it[1]) > d or abs(it[0] - it[2]) > d or abs(it[2]-it[1]) > d:
#         return False
#     return True
# print(len(list(filter(filt, may))))


"""
https://www.nowcoder.com/test/question/done?tid=33050607&qid=362292#summary
1 1 1 2 2 2 6 6 6 7 7 7 9 9 可以组成1,2,6,7的4个刻子和9的雀头，可以和牌
1 1 1 1 2 2 3 3 5 6 7 7 8 9 用1做雀头，组123,123,567,789的四个顺子，可以和牌
1 1 1 2 2 2 3 3 3 5 6 7 7 9 无论用1 2 3 7哪个做雀头，都无法组成和牌的条件。
1 1 1 2 2 2 5 5 5 6 6 6 9





"""









"""
蜜汁猫咪特征
1
8
2 1 1 2 2
2 1 1 1 4
2 1 1 2 2
2 2 2 1 4
0
0
1 1 1
1 1 1
"""
case_n = int(input())
for i in range(case_n):
    frame_n = int(input())
    dic = {}
    for frame in range(frame_n):
        line = input().split()
        feature_n = line[0]
        if feature_n == 0:
            continue
        for feature in range(feature_n):
            x = line[feature * 2 + 1]
            y = line[feature * 2 + 2]
            if [x, y] in dic:
                continue
            else:
                dic[]

# n = int(input())
#
# while n > 0:
#     m = int(input())
#     res = 1
#     d = {}
#     for i in range(m):
#         l = list(map(int, input().split()))
#         k = l[0]
#         tmp_d = {}
#         for j in range(k):
#             index = l[2 * j + 1] * 1000000000 + l[2 * j + 2]
#             if index in d:
#                 tmp_d[index] = d[index] + 1
#                 res = max(res, tmp_d[index])
#             else:
#                 tmp_d[index] = 1
#         d = tmp_d
#     print(res)
#     n -= 1









