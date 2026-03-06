"""
185.452. Minimum Number of Arrows to Burst Balloons



There are a number of spherical balloons spread in two-dimensional space. For each 
alloon, provided input is the start and end coordinates of the horizontal diameter. 
Since it's horizontal, y-coordinates don't matter and hence the x-coordinates of start 
and end of the diameter suffice. Start is always smaller than end. There will be at most 104 balloons.

An arrow can be shot up exactly vertically from different points along the x-axis.
A balloon with xstart and xend bursts by an arrow shot at x if xstart ≤ x ≤ xend. 
There is no limit to the number of arrows that can be shot. An arrow once shot keeps 
travelling up infinitely. The problem is to find the minimum number of arrows that must be shot to burst all balloons.

Example:

Input:
[[10,16], [2,8], [1,6], [7,12]]

Output:
2

Explanation:
One way is to shoot one arrow for example at x = 6 (bursting the balloons [2,8] and 
[1,6]) and another arrow at x = 11 (bursting the other two balloons).


"""


def findMinArrowShots(self, points: List[List[int]]) -> int:
    if not points:
        return 0
    
    # sort by x_end
    points.sort(key = lambda x : x[1])
    
    arrows = 1
    first_end = points[0][1]
    for x_start, x_end in points:
        # if the current balloon starts after the end of another one,
        # one needs one more arrow
        if first_end < x_start:
            arrows += 1
            first_end = x_end
    
    return arrows



def findMinArrowShots(self, points: List[List[int]]) -> int:
    size = len(points)
    # 特判
    if size < 2:
        return size
    # 按照区间的起始端点排序
    points.sort(key=lambda x:x[0])
    
    # 只要有区间就至少需要一只箭
    res = 1
    # 最远距离：使用当前这只箭能引爆气球的最远距离
    end = points[0][1]
    
    for i in range(1, size):
        if points[i][0] > end:
            end = points[i][1]
            res += 1
        else:
            end = min(end, points[i][1])
    return res



def findMinArrowShots(self, points: List[List[int]]) -> int:
    n = len(points)
    if n == 0: return 0
    dp = [1] * n
    cnt = 1
    points.sort(key=lambda a:a[1])

    for i in range(n):
        for j in range(0, i):
            if points[i][0] > points[j][1]:
                dp[i] = max(dp[i], dp[j] + 1)
                cnt = max(cnt, dp[i])
    return cnt


























































































