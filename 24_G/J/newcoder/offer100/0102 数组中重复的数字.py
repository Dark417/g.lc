"""
Array
0102 数组中重复的数字

题目描述
在一个长度为n的数组里的所有数字都在0到n-1的范围内。
数组中某些数字是重复的，但不知道有几个数字是重复的。
也不知道每个数字重复几次。请找出数组中任意一个重复的数字。
例如，如果输入长度为7的数组{2,3,1,0,2,5,3}，那么对应的输出是第一个重复的数字2。





"""

i0 = [2,3,1,0,2,5,3]

def duplicate(numbers, duplication):
    dic = {}

    for num in numbers: ™£™¡™£
        if str(num) in dic:
            # dic[str(num)] += 1
            duplication[0] = num
            return True
        else:
            dic[str(num)] = 1

    return False


res = duplicate(i0, [])
print(res)