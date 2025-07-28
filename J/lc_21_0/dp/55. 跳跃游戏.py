# 55. 跳跃游戏


def canJump(self, nums: List[int]) -> bool:
    n = len(nums)
    dis = 0
    for i in range(n):
        if i <= dis:
            dis = max(dis, nums[i] + i)
            if dis >= n-1:
                return True
    return False






















