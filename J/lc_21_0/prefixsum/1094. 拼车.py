# 1094. 拼车

def carPooling(self, trips: List[List[int]], capacity: int) -> bool:
    f = [0 for _ in range(1002)]

    for x, L, R in trips:       #差分统计的思想   台阶，上下楼梯的思想
        f[L] += x
        f[R] -= x
        
    if f[0] > capacity:
        return False
    for i in range(1, 1002):
        f[i] = f[i-1] + f[i]
        if f[i] > capacity:
            return False
    
    return True


from itertools import accumulate, dropwhile

class Solution:
    def carPooling(self, trips: List[List[int]], capacity: int) -> bool:
        numberOfPeople = [0] * 1001
        for number, start, end in trips:
            numberOfPeople[start] += number
            numberOfPeople[end] -= number
        return not list(dropwhile(lambda x: x <= capacity, accumulate(numberOfPeople)))



def carPooling(self, trips: List[List[int]], capacity: int) -> bool:
    events = [[t[1],t[0]] for t in trips] + [[t[2],-t[0]] for t in trips]
    events.sort()
    count = 0
    for _,n in events:
        count +=n
        if count > capacity:
            return False
    return True


def carPooling(self, trips: List[List[int]], capacity: int) -> bool:
    moves = []
    for trip in trips:
        moves.append((trip[1], trip[0]))
        moves.append((trip[2], -trip[0]))
    moves.sort()
    
    total = 0
    for move in moves:
        total += move[1]
        if total > capacity:
            return False
    return True





from typing import List
import heapq


class Solution:
    def carPooling(self, trips: List[List[int]], capacity: int) -> bool:
        trips.sort(key=lambda x: x[1])
        off_dist = []
        count = 0
        for i in range(len(trips)):
            dist = trips[i][1]
            while off_dist and dist >= off_dist[0][0]:
                _, passenger = heapq.heappop(off_dist)
                count -= passenger
            count += trips[i][0]
            if count > capacity:
                return False
            heapq.heappush(off_dist, [trips[i][-1], trips[i][0]])
        return True


    def carPooling1(self, trips: List[List[int]], capacity: int) -> bool:
        stop = []
        for n, s, e in trips:
            stop.append([s, n])
            stop.append([e, -n])

        stop.sort()

        for _, count in stop:
            capacity -= count
            if capacity < 0: return False

        return True


















