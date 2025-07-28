# 7. 整数反转


def reverse(self, x: int) -> int:
    n = x if x > 0 else abs(x)
    res = 0

    while n >= 1:
        d = n % 10
        if d != 0:
            res = res*10 + d
        elif res > 0:
            res = res*10

        n //= 10

    res = -1 * res if x < 0 else res
    return res if -2147483648 < res < 2147483647 else 0





def reverse_force(self, x: int) -> int:
    if -10 < x < 10:
        return x
    str_x = str(x)
    if str_x[0] != "-":
        str_x = str_x[::-1]
        x = int(str_x)
    else:
        str_x = str_x[:0:-1]
        x = int(str_x)
        x = -x
    return x if -2147483648 < x < 2147483647 else 0










