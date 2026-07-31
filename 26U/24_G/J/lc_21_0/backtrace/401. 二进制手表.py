# 401. 二进制手表


def readBinaryWatch(self, n):
    def dfs(n, hours, mins, idx):
        if hours >= 12 or mins > 59: return
        if not n:
            res.append(str(hours) + ":" + "0" * (mins < 10) + str(mins))
            res.append("{}:{:02}".format(hours, mins))
            return
        for i in range(idx, 10):
            if i < 4: 
                dfs(n - 1, hours | (1 << i), mins, i + 1)
            else:
                k = i - 4
                dfs(n - 1, hours, mins | (1 << k), i + 1)
    res = []
    dfs(n, 0, 0, 0)
    return res


#02d formats an integer (d) to a field of minimum width 2 
#(2), with zero-padding on the left (leading 0)


class Solution:
    _LED_NUM = 10
    _HOUR_LED_NUM = 4

    # Backtracking
    def __init__(self):
        self._times = []

    def readBinaryWatch(self, num: int):
        self._backtrack(num, 0, 0, 0)
        return self._times
    
    def _backtrack(self, num: int, pos: int, hour: int, minute: int):
        if hour > 11 or minute > 59:
            return
        elif num == 0:
            self._times.append("{:d}:{:02d}".format(hour, minute))
            return

        for i in range(pos, Solution._LED_NUM):
            if i < Solution._HOUR_LED_NUM:
                self._backtrack(num - 1, i + 1,
                    hour + 2**i, minute)
            else:
                self._backtrack(num - 1, i + 1,
                    hour, minute + 2**(i - Solution._HOUR_LED_NUM))



def readBinaryWatch(self, num):
    return ['%d:%02d' % (h, m)
            for h in range(12) for m in range(60)
            if (bin(h) + bin(m)).count('1') == num]




def readBinaryWatch(self, num):
    res = []
    for Hs in range(0, min(num, 4) + 1):
        Ms = num - Hs
        if not 0 <= Ms <= 6: continue
        hcomb = itertools.combinations(range(4), Hs)
        mcomb = itertools.combinations(range(6), Ms)
        hcomb = tuple(map(lambda hs: 0 + sum(2 ** i for i in hs), hcomb))
        mcomb = tuple(map(lambda ms: 0 + sum(2 ** i for i in ms), mcomb))
        res += ['{}:{:02d}'.format(h, m) for h in hcomb
                for m in mcomb if h < 12 and m < 60]
    return res











