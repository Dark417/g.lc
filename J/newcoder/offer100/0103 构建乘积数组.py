"""
Array
0103 构建乘积数组

题目描述
给定一个数组A[0,1,...,n-1],
请构建一个数组B[0,1,...,n-1],
其中B中的元素B[i]=A[0]*A[1]*...*A[i-1]*A[i+1]*...*A[n-1]。
不能使用除法。（注意：规定B[0] = A[1] * A[2] * ... * A[n-1]，B[n-1] = A[0] * A[1] * ... * A[n-2];）

1. brute force
2. dynamic programming

"""
from itertools import product

input0 = [1, 2, 3, 4]

# i = len(input0[2:])
# print(i)






# 23ms
def multiply(self, A):
    # write code here
    head = [1]
    tail = [1]
    for i in range(len(A)-1):
        head.append(A[i]*head[i])
        tail.append(A[-i-1]*tail[i])
    return [head[j]*tail[-j-1] for j in range(len(head))]


def multiply(self, A):
    # write code here
    if not A:
        return []
    # 计算前面一部分
    num = len(A)
    B = [None] * num
    B[0] = 1
    for i in range(1, num):
        B[i] = B[i-1] * A[i-1]
    # 计算后面一部分
    # 自下而上
    # 保留上次的计算结果乘本轮新的数,因为只是后半部分进行累加，所以设置一个tmp,能够保留上次结果
    tmp = 1
    for i in range(num-2, -1, -1):
        tmp *= A[i+1]
        B[i] *= tmp
    return B


def multiply(self, A):
    # write code here
    B=A[:]
    number=0
    for m in range(len(A)):
        sum=1
        number=m
        for n in range(len(A)):
            if n!=number:
                sum=sum*A[n]
        B[number]=sum
    return B


def multiply(self, A):
    B = [1 for i in range(len(A))]
    for i in range(1, len(A)):
        tempA = A[i:] + A[:i]
        for j in range(len(B)):
            B[j] = B[j] * tempA[j]
    return B


def multiply(self, A):
    # write code here
    B = A[:]
    number = 0
    for m in range(len(A)):
        sum = 1
        number = m
        for n in range(len(A)):
            if n != number:
                sum = sum * A[n]
        B[number] = sum
    return B


# 26ms
def multiply(self, A):
    # write code here
    length = len(A)
    if(length == 0):
        return []
    import copy
    B = copy.copy(A)
    B[0] = 1
    # 计算下三角连乘
    for i in range(1,length):
        B[i] =  B[i-1] * A[i-1]
    # 计算下三角连乘
    temp = 1
    for j in range(length-2,-1,-1):
        temp *= A[j+1]
        B[j] *= temp
    return B


# A[i] = 1
def multiply(self, A):
        # write code here
        length = len(A)
        B = []
        if(length == 0):
            return B
        for i in range(length):
            temp = A[i]
            A[i] = 1
            Bi = 1
            for j in A:
                Bi *= j
            B.append(Bi)
            A[i] = temp
        return B


# D iterate A through except for i
def multiply1(A):
    B = [None] * len(A)

    for i in range(len(A)):
        pdt = 1
        for j in range(len(A[:i])):
            pdt *= A[j]

        for j in range(len(A[i+1:])):
            pdt *= A[j+i+1]
        B[i] = pdt
    return B


# problem, won't handle 0
def multiply(A):
    pdt = 1
    B = [1] * len(A)
    for i in A:
        pdt *= i

    for i in range(len(A)):
        B[i] = int(pdt / A[i])

    return B


res = multiply1(input0)
print(res)
