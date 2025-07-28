# 75. 颜色分类

# single pointer
def sortColors(self, nums: List[int]) -> None:
    n = len(nums)
    ptr = 0
    for i in range(n):
        if nums[i] == 0:
            nums[i], nums[ptr] = nums[ptr], nums[i]
            ptr += 1
    for i in range(ptr, n):
        if nums[i] == 1:
            nums[i], nums[ptr] = nums[ptr], nums[i]
            ptr += 1


# 2pointer
def sortColors(self, nums: List[int]) -> None:
    n = len(nums)
    p0 = p1 = 0
    for i in range(n):
        if nums[i] == 1:
            nums[i], nums[p1] = nums[p1], nums[i]
            p1 += 1
        elif nums[i] == 0:
            nums[i], nums[p0] = nums[p0], nums[i]
            if p0 < p1:
                nums[i], nums[p1] = nums[p1], nums[i]
            p0 += 1
            p1 += 1



def sortColors(self, nums: List[int]) -> None:
    def swap(nums, index1, index2):
        nums[index1], nums[index2] = nums[index2], nums[index1]

    size = len(nums)
    if size < 2:
        return

    zero = 0
    two = size
    i = 0
    while i < two:
        if nums[i] == 0:
            swap(nums, i, zero)
            i += 1
            zero += 1
        elif nums[i] == 1:
            i += 1
        else:
            two -= 1
            swap(nums, i, two)


def sortColors(self, nums: List[int]) -> None:
    n = len(nums)
    p0, p2 = 0, n - 1
    i = 0
    while i <= p2:
        while i <= p2 and nums[i] == 2:
            nums[i], nums[p2] = nums[p2], nums[i]
            p2 -= 1
        if nums[i] == 0:
            nums[i], nums[p0] = nums[p0], nums[i]
            p0 += 1
        i += 1


def sortColors(self, nums: List[int]) -> None:
    i, j = 0, len(nums)-1
    
    while i <= j:
        if nums[i] != 0:
            nums[i], nums[j] = nums[j], nums[i]
            j -= 1
        else:
            i += 1

    j = len(nums)-1
    while i < j:
        if nums[i] != 1:
            nums[i], nums[j] = nums[j], nums[i]
            j -= 1
        else:
            i += 1