"""
2020.4.27
alibaba_test

#!/usr/bin/env python
# coding=utf-8
# Python使用的是3.4.3，缩进可以使用tab、4个空格或2个空格，但是只能任选其中一种，不能多种混用
while 1:
  a=[]
  s = input()

  if s != "":
    for x in s.split():
      a.append(int(x))
        print(sum(a))
    else:
        break

"""

# while True:
#     try:
#         a, b = map(int, input().split())
#         print(a + b)
#     except:
#         break

# while True:
#     try:
#         input_list = list(map(int, input().split(' ')))
#         result = input_list[0] + input_list[1]
#         print(result)
#     except:
#         break


# while True:
#     try:
#         a, b = map(int, input().split())
#         print(a + b)
#     except:
#         break

# while True:
#     try:
#         a = input()
#         if a:
#             print(a)
#         else:
#             break
#     except:
#         break

# a + b
# import sys
# try:
#     while True:
#         line = sys.stdin.readline().strip()
#         if line == '':
#             break
#         lines = line.split()
#         print(int(lines[0])+ int(lines[1]))
#         #for i in lines:
#          #   print(int(lines[0] + int(lines[1])))
# except:
#     pass

# a + b
# import sys
# while True:
#     try:
#         line = sys.stdin.readline().strip()
#         if line == '':
#             break
#         lines = line.split()
#         # print(lines)
#         print(int(lines[0]) + int(lines[1]))
#     except:
#         pass


# import sys
# # for line in sys.stdin:
# #     print(line)
# #     a = line.split()
# #
# #     # if len(a) == 1:
# #     #     print('rua')
# #     # else:
# #     #     print(a)
# #
# # #
# # import sys
# # try:
# #     while True:
# #         line = sys.stdin.readline().strip()
# #         if line == '':
# #             break
# #         i = line.split()
# #         print(i)
# # except:
# #     pass



# a = [2, 1, 3]
# print(a.sort())



import sys

dic = {}
l_ord = []

for line in sys.stdin:
    a = line.split()
    if len(a) == 1:
        n_lines = int(a[0])
        # print(n_lines)
    else:
        # print(a)
        l_ord.append(int(a[0]))
        # l.append[a]
        dic[a[0]] = [int(a[0]), int(a[1])]

# print(l_ord.sort())

def leave_time(end, start):
    if
    return leave

l_ord.sort()
for i in range(0, len(l_ord) - 1):
    leave = leave_time(dic[i][1] - dic[i][0])
    if leave < dic[i][1]:
        next
    else:
        print(-1)
        break
print(1)















