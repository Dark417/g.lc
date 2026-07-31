400. 第 N 位数字
"""
9 * 1
90 * 2
...
presum

"""

def totalDigits(self, length: int) -> int:
    digits = 0
    curCount = 9
    for curLength in range(1, length + 1):
        digits += curLength * curCount
        curCount *= 10
    return digits

def findNthDigit(self, n: int) -> int:
    low, high = 1, 9
    while low < high:
        mid = (low + high) // 2
        if self.totalDigits(mid) < n:
            low = mid + 1
        else:
            high = mid
    d = low
    prevDigits = self.totalDigits(d - 1)
    index = n - prevDigits - 1
    start = 10 ** (d - 1)
    num = start + index // d
    digitIndex = index % d
    return num // 10 ** (d - digitIndex - 1) % 10


"""
public int findNthDigit(int n) {
    int low = 1, high = 9;
    while (low < high) {
        int mid = (high - low) / 2 + low;
        if (totalDigits(mid) < n) {
            low = mid + 1;
        } else {
            high = mid;
        }
    }
    int d = low;
    int prevDigits = totalDigits(d - 1);
    int index = n - prevDigits - 1;
    int start = (int) Math.pow(10, d - 1);
    int num = start + index / d;
    int digitIndex = index % d;
    int digit = (num / (int) (Math.pow(10, d - digitIndex - 1))) % 10;
    return digit;
}

public int totalDigits(int length) {
    int digits = 0;
    int curLength = 1, curCount = 9;
    while (curLength <= length) {
        digits += curLength * curCount;
        curLength++;
        curCount *= 10;
    }
    return digits;
}



"""

def findNthDigit(self, n: int) -> int:
    d, count = 1, 9
    while n > d * count:
        n -= d * count
        d += 1
        count *= 10
    index = n - 1
    start = 10 ** (d - 1)
    num = start + index // d
    digitIndex = index % d
    return num // 10 ** (d - digitIndex - 1) % 10


