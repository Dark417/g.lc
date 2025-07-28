"""
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
#     line = input()
#     if line:
#         if len(line) <= 3:
#             if int(line) <= 0:
#                 res = "($" + line + ")"
#                 print(res)
#             else:
#                 res = "$" + line
#                 print(res)
#         else:
#             num = int(line)
#             qt = len(line) // 3
#             rmd = len(line) % 3
#
#             res = ''
#             res_string = ''
#
#             length = len(line)
#             while length > 3:
#                 res = line[-3:]
#                 res_string = "," + res + res_string
#                 qt -= 1
#                 line = line[:-3]
#
#             if num < 0:
#                 res_string = "($" + res_string + ")"
#                 print(res_string)
#             else:
#                 res_string = "$" + res_string + ""
#                 print(res_string)
#     else:
#         break
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
import sys
try:
    while True:
        line = sys.stdin.readline().strip()
        if line == '':
            break
        i = line.split()
        print(i)
except:
    pass


while True:
    try:
        n = int(input())
        nums = list(map(int, input().split()))
        ks = int(input())
        res = []
        print(n)
        print(nums)
    except:
        break





















