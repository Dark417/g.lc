# 1109. 航班预订统计


def corpFlightBookings(self, bookings: List[List[int]], n: int) -> List[int]:
    res = [0] * n
    for l, r, c in bookings:
        res[l-1] += c
        if r < n:
            res[r] -= c
    for i in range(1, n):
        res[i] += res[i-1]
    return res



def corpFlightBookings(self, bookings: List[List[int]], n: int) -> List[int]:
    bookings.sort()
    res = [0] * n
    for booking in bookings:
        for i in range(booking[0]-1, booking[1]):
            res[i] += booking[2]
    return res



















