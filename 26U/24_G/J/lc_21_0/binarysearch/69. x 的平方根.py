# 69. x 的平方根

def mySqrt(self, x: int) -> int:
    l, r, ans = 0, x, -1
    l, r, ans = 0, x//2 + 1, -1
    while l <= r:
        mid = (l + r) // 2
        if mid * mid <= x:
            ans = mid
            l = mid + 1
        else:
            r = mid - 1
    return ans



def mySqrt(self, x: int) -> int:
    # 为了照顾到 0 把左边界设置为 0
    left = 0
    # 为了照顾到 1 把右边界设置为 x // 2 + 1
    right = x // 2 + 1
    while left < right:
        # 注意：这里一定取右中位数，如果取左中位数，代码可能会进入死循环
        # mid = left + (right - left + 1) // 2
        mid = (left + right + 1) >> 1

        if mid * mid > x:
            right = mid - 1
        else:
            left = mid
    # 因为一定存在，因此无需后处理
    return left



def mySqrt(self, x: int) -> int:
    if x == 0:
        return 0

    left = 1
    right = x // 2

    while left < right:
        # 注意：这里一定取右中位数，如果取左中位数，代码可能会进入死循环
        # mid = left + (right - left + 1) // 2
        mid = (left + right + 1) >> 1
        square = mid * mid

        if square > x:
            right = mid - 1
        else:
            left = mid
    # 因为一定存在，因此无需后处理
    return left





















































