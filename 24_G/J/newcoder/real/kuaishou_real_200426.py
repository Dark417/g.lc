"""
2020.4.25
REAL!



"""

"""

"""
# import sys
# try:
#     while True:
#         line = sys.stdin.readline().strip()
#         if line == '':
#             break
#         i = line.split()
#         print(i)
# except:
#     pass
#
#
# while True:
#     try:
#         n = int(input())
#         nums = list(map(int, input().split()))
#         ks = int(input())
#
#         l = list(map(str, input()))
#         # res = []
#         # res.append(max(nums[:ks]))
#         # for i in range(1, n - ks + 1):
#         #     if nums[i-1] == res[-1]:
#         #         res.append(max(nums[i:i+ks]))
#         #     else:
#         #         res.append(max(res[-1], nums[i + ks - 1]))
#         # res = [str(i) for i in res]
#         # print(' '.join(res))
#     except:
#         break
#
#
# import sys
# matrix = []
#
#
# try:
#     while True:
#         line = sys.stdin.readline().strip()
#         if line == '':
#             break
#
#
#         line = (list(line))
#         matrix.append(line)
#         # print(matrix)
# except:
#     pass
#
#
# import sys
# for line in sys.stdin:
#     a = line.split()
#     print(int(a[0]) + int(a[1]))
#
#
# import sys
# if __name__ == "__main__":
#     # 读取第一行的n
#     n = int(sys.stdin.readline().strip())
#     ans = 0
#     for i in range(n):
#         # 读取每一行
#         line = sys.stdin.readline().strip()
#         # 把每一行的数字分隔后转化成int列表
#         values = list(map(int, line.split()))
#         for v in values:
#             ans += v
#     print(ans)

# 1
# n = int(input().strip())
# urls = [None] * n
#
# for i in range(n):
#     line = input().strip()
#     urls[i] = line
#
# for i in urls:
#     print(i)

# 1
import sys

if __name__ == "__main__":
    n = int(sys.stdin.readline().strip())
    urls = [None] * n

    for i in range(n):
        line = sys.stdin.readline().strip()
        urls[i] = line

num = 0
domain_list = []
dic = {}

for i in urls:
    full = i.split("//")[1]
    x = full.split("/")

    if len(x) == 1:
        path = ""
    else:
        path = ""
        for u in range(1, len(x)):
            path += full.split("/")[u]
    domain = full.split("/")[0]
    # print(domain)
    # print(path)

    if domain not in domain_list:
        domain_list += domain
        dic[domain] = [path]
        # print("domain: ", domain, " add path: ", path)
    else:
        if path not in dic[domain]:
            dic[domain].append(path)

        # print("domain: ", domain, " add path: ", path)
# print(domain_list)
# print(dic)
print(domain_list)
res_num = 0
result = []
for i in domain_list:
    for j in domain_list:
        if i != j:
            print(i)
            print(j)
            print()
            if len(dic[i]) == len(dic[j]):
                for x in dic[i]:
                    if x not in dic[j]:
                        continue
                for y in dic[j]:
                    if y not in dic[i]:
                        continue
                res_num += 1
                result += i
                print(result)
print(res_num)
print(i for i in result)

# # 2
# n = int(input().strip())
# moves = [None] * n
#
# for i in range(n):
#     move = input().strip()
#     moves += move
#
# # 3
#
#
# # 4
# n = int(input().strip())
# x = n[0]
# y = n[1]
# print(x)
# print(y)
# moves = [None] * n
#
# for i in range(n):
#     move = input().strip()
#     moves += move
