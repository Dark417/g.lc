"""
Array
0101 二维数组中的查找


题目描述
在一个二维数组中（每个一维数组的长度相同），每一行都按照从左到右递增的顺序排序，
每一列都按照从上到下递增的顺序排序。请完成一个函数，输入这样的一个二维数组和一个整数，
判断数组中是否含有该整数。


1. bf
2. bs
pick mid of mid

3. stairs?

"""


#
def find(target, array):











# bf
def find(target, array):
    for i in array:
        if target in i:
            return True
        # else:
        #     continue
    return False


def find(target, array):
    for i in range(len(array)):
        # if target in array[i]:    # work
        for j in range(len(array[i])):

            if array[i][j] == target:
                return True
    return False
