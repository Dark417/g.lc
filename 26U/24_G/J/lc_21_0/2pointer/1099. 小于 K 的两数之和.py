# 1099. 小于 K 的两数之和

def twoSumLessThanK(self, A: List[int], K: int) -> int:
    # 1. 暴力for循环
    # ans = -1
    # for i in range(len(A) - 1):
    #     for j in range(i+1, len(A)):
    #         if A[i] + A[j] < K:
    #             ans = max(ans, A[i] + A[j])
    # return ans
    
    # 2. 排序 + 双指针法
    ans, N = -1, len(A)
    left, right = 0, N - 1
    A.sort()
    while left < right:
        S = A[left] + A[right]
        if S < K:
            ans = max(ans, S)
            left += 1
        else:
            right -= 1
    return ans 






