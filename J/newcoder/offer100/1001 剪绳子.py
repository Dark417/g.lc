"""
1001 剪绳子
dynamic programming

题目描述
给你一根长度为n的绳子，请把绳子剪成整数长的m段（m、n都是整数，n>1并且m>1），
每段绳子的长度记为k[0],k[1],...,k[m]。
请问k[0]xk[1]x...xk[m]可能的最大乘积是多少？
例如，当绳子的长度是8时，我们把它剪成长度分别为2、3、3的三段，
此时得到的最大乘积是18。

"""


def cutRope(number):
    pdt = 1

    if number == 2:
        return 1

    if number == 3:
        return 2

    while number > 5:
        number -= 3
        pdt *= 3

    if number == 5:
        number -= 3
        pdt *= 3

    if number == 3:
        pdt *= 3

    if number == 4:
        number -= 2
        pdt *= 2

    if number == 2:
        pdt *= 2

    return pdt


def cutRope(number):
    l = []
    pdt = 1

    while number > 5:
        number = number - 2
        l.append(2)
        pdt *= 2

    if number == 5 or number == 3:
        l.append(3)
        pdt *= 2

    if number == 4 or number == 2:
        l.append(2)
        pdt *= 2

    return pdt
