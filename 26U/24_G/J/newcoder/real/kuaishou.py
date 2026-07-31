"""
2020.4.25
Newcoder
real
kuaishou
快手2020校园招聘秋招笔试--算法C试卷
20 choice
4 programming
"""

"""
1
"""

"""
2
"""

"""
3
"""

# import sys
# dic = {}
# l_ord = []
#
# for line in sys.stdin:
#     a = line.split()
#     if len(a) == 1:
#         n_lines = int(a[0])
#         # print(n_lines)
#     else:
#         # print(a)
#         l_ord.append(int(a[0]))
#         # l.append[a]
#         dic[a[0]] = [int(a[0]), int(a[1])]
#
# # print(l_ord.sort())
#
# def leave_time(end, start):
#     if
#     return leave
#
# l_ord.sort()
# for i in range(0, len(l_ord) - 1):
#     leave = leave_time(dic[i][1] - dic[i][0])
#     if leave < dic[i][1]:
#         next
#     else:
#         print(-1)
#         break
# print(1)




"""
4
最近月神需要在移动端部署一个卷积神经网络模型,但是月神碰到了一个问题,
即月神使用了一个核非常大的最大池化(max-pooling)操作,但现有推理引擎不支持这一操作,
作为月神的好朋友,你能帮帮月神么。
所谓max-pooling,指的是给定一个数组（为了简化问题,暂定数组为一维）,
在每一个滑动窗口内找出最大的那个数,举例如下：
假设数组为[16, 19, 15, 13, 16, 20],且核大小为3,则当窗口依次滑过数组时,
取出如下4个子数组：
[16, 19, 15], [19, 15, 13], [15, 13, 16], [13, 16, 20],
这4个子数组中的最大值分别为19, 19, 16, 20,
故该数组经过大小为3的核的max-pooling的结果为19 19 16 20.

输入描述:
输入由三行构成

第一行是一个整数n，  给出数组中元素个数

第二行是n个整数，     给出数组中的元素
第三行是一个整数 ks , 给出max-pooling核的大小

输出描述:
输出一行（没有换行符）

输出给定数组及给定核大小的后，max-pooling的结果,

每两个整数之间加一个空格

输入例子1:
5
31 24 21 14 22
1

输出例子1:
31 24 21 14 22

输入例子2:
5
18 14 31 1 26
2

输出例子2:
18 31 31 26

输入例子3:
16
61 53 2 13 51 30 48 44 58 46 36 8 2 8 34 10
7

输出例子3:
61 53 58 58 58 58 58 58 58 46
"""
# dis
while True:
    try:
        n = int(input())
        nums = list(map(int, input().split()))
        ks = int(input())
        res = []
        res.append(max(nums[:ks]))
        for i in range(1, n - ks + 1):
            if nums[i-1] == res[-1]:
                res.append(max(nums[i:i+ks]))
            else:
                res.append(max(res[-1], nums[i + ks - 1]))
        res = [str(i) for i in res]
        print(' '.join(res))
    except:
        break



import sys

dic = {}
l = []


for line in sys.stdin:
    a = line.split()
    b = map(int, a)
    l.append(b)
    i += 1
print(l)


def P(x):
    y = reduce(lambda x, y: x * y, map(int, str(x)))
    return y and not x % y
def Q(x):
    return P(x) and P(x + 1)
print (sum(Q(x) for x in range(2019)))






