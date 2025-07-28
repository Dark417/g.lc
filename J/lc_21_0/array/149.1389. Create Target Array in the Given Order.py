"""
149.1389. Create Target Array in the Given Order
按既定顺序创建目标数组


"""



def createTargetArray(self, nums: List[int], index: List[int]) -> List[int]:
    l = []
    for i in range(len(index)):
        l.insert(index[i], nums[i])
    return l

def createTargetArray(self, nums: List[int], index: List[int]) -> List[int]:
    target =[]
    for i in range(len(nums)):
        if index[i] == len(target) :
            target.append(nums[i])
        else:
            target = target[:index[i]] + [nums[i]] + target[index[i]:]
    return target


def createTargetArray(self, nums: List[int], index: List[int]) -> List[int]:
    res = []
    for i in range(len(index)):
        res = res[:index[i]] + [nums[i]] + res[index[i]:]
    return res

# 把index需要插入的绝对顺序排出来，然后再往里插入












































