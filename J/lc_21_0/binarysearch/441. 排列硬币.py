# 441. 排列硬币

def arrangeCoins(self, n: int) -> int:
    k = 1
    sm = 0
    while sm + k <= n:
        sm += k
        k += 1
    return k - 1



def arrangeCoins(self, n: int) -> int:
    l, r = 0, n   # 1 ok
    
    while l <= r:
        mid = (l + r) // 2
        sm = (mid + 1) * mid / 2
        if sm == n:
            return int(mid)
        if sm < n:
            l = mid + 1
        else:
            r = mid - 1
        
    return r



"""

public int arrangeCoins(int n) {
    int low = 0, high = n;
    while (low <= high) {
        long mid = (high - low) / 2 + low;
        long cost = ((mid + 1) * mid) / 2;
        if (cost == n) {
            return (int)mid;
        } else if (cost > n) {
            high = (int)mid - 1;
        } else {
            low = (int)mid + 1;
        }
    }
    return high;
}






根据数学公式，k(k+1) /2 = n，可以得到其正数解为：k = sqrt(2n+1/4) - 1/2。然后求整即可。
唯一的问题是，这里2n+1/4有可能会超出sqrt函数的参数范围。
于是，我们可以变换一下， k = sqrt(2) * sqrt(n+1/8) - 1/2，这样求平方根就不会超限了。



public int arrangeCoins(int n) {
    return (int)(Math.sqrt(2) * Math.sqrt(n + 0.125) - 0.5);
}



"""


























