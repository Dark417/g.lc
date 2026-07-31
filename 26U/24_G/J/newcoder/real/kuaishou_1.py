"""
2020.4.25
Newcoder
real
kuaishou
快手2020校园招聘秋招笔试--算法B试卷


21.
给定一个数独板的输入，确认当前的填法是否合法。
合法的输入需要满足以下三个条件：
1. 每一行的9个格子中是1-9的9个数字，且没有重复
2. 每一列的9个格子中是1-9的9个数字，且没有重复
3. 9个3*3的小格子中是1-9的9个格子，且没有重复


输入描述:
输入9行字符串，每行9个字符（不包含\r\n)，总共81个字符，空着的格子用字符‘X’表示

53XX7XXXX
6XX195XXX
X98XXXX6X
8XXX6XXX3
4XX8X3XX1
7XXX2XXX6
X6XXXX28X
XXX419XX5
XXXX8XX79

输出描述:
合法在输出字符串，“true”
非法则输出字符串，“false”

输入例子1:
53XX7XXXX
6XX195XXX
X98XXXX6X
8XXX6XXX3
4XX8X3XX1
7XXX2XXX6
X6XXXX28X
XXX419XX5
XXXX8XX79

输出例子1:
true
"""

import sys
matrix = []


try:
    while True:
        line = sys.stdin.readline().strip()
        if line == '':
            break


        line = (list(line))
        matrix.append(line)
        # print(matrix)
except:
    pass


nums = "123456789"
dic = {}


def check_row(matrix):
    for i in matrix:
        for j in i:
            if j == "X":
                continue
            if j in dic:
                return False
            else:
                dic[j] = 1
    return True

def check_col(matrix):
    for i in range(0, 9):
        for j in range(0, 9):
            if matrix[j][i] == "X":
                continue
            if matrix[j][i] in dic:
                return False
            else:
                dic[matrix[j][i]] = 1
    return True

def check_grid(matrix):
    for i in range(1, 4):
        for j in range(1, 4):



    return True

def check_val(matrix):

    if check_row(matrix) == 0 or check_col(matrix) == 0 or check_grid(matrix) == 0:
        return False
    return True

print(check_val(matrix))


"""
22. [编程题]质因数统计
我们知道每一个大于1的整数都一定是质数或者可以用质数的乘积来表示，
如10=2*5。现在请设计一个程序，对于给定的一个(1，N] 之间的正整数（N取值不超过10万），
你需要统计(1，N] 之间所有整数的质数分解后，所有质数个数的总个数。举例，输入数据为6，
那么满足(1,6] 的整数为2，3，4，5，6，
各自进行质数分解后为：2=>2，3=>3，4=>2*2，5=>5，6=>2*3。
对应的质数个数即为1，1，2，1，2。最后统计总数为7



输入描述:
输入数据包含1行，为一个大于1的整数（不超过10万）。

输出描述:
输出小于等于该数的所有整数质数分解后的总个数。

输入例子1:
6

输出例子1:
7

"""

b = 1
def a():
    print(1)
    b += 1
print(b)
number = int(input())
prime_list = []

def div_prime(n):


    return n


for num in range(2, number + 1):

    for prime in prime_list:
        #can divide
        if  num % prime == 0:
            continue




print(res)



"""
23. [编程题]Levenshtein distance
已知两个字符串strA和strB，求将strA转换成strB所需的最小编辑操作次数。许可的编辑操作包括将一个字符替换成另一个字符，插入一个字符，删除一个字符。

输入描述:
任意字符串strA和strB，其中第一行为strA，第二行为strB

输出描述:
最小编辑操作次数

输入例子1:
FreshMeat
FishAndMeat

输出例子1:
5


"""