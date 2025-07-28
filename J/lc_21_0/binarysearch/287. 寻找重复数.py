# 287. 寻找重复数


def longestOnes(self, nums: List[int], k: int) -> int:
    n = len(nums)
    P = [0]
    for num in nums:
        P.append(P[-1] + (1 - num))
    
    ans = 0
    for right in range(n):
        left = bisect.bisect_left(P, P[right + 1] - k)
        ans = max(ans, right - left + 1)
    
    return ans



def findDuplicate(self, nums: List[int]) -> int:
    size = len(nums)
    left = 0
    right = size - 1

    while left < right:
        mid = left + (right - left) // 2

        cnt = 0
        for num in nums:
            if num <= mid:
                cnt += 1
        # 根据抽屉原理，小于等于 4 的数的个数如果严格大于 4 个，
        # 此时重复元素一定出现在 [1, 4] 区间里

        if cnt > mid:
            # 重复的元素一定出现在 [left, mid] 区间里
            right = mid
        else:
            # if 分析正确了以后，else 搜索的区间就是 if 的反面
            # [mid + 1, right]
            left = mid + 1
    return left     



def findDuplicate(self, nums):
    nums.sort()
    for i in range(1, len(nums)):
        if nums[i] == nums[i-1]:
            return nums[i]



def findDuplicate(self, nums):
    seen = set()
    for num in nums:
        if num in seen:
            return num
        seen.add(num)






"""
public int findDuplicate(int[] nums) {
    int n = nums.length;
    int l = 1, r = n - 1, ans = -1;
    while (l <= r) {
        int mid = (l + r) >> 1;
        int cnt = 0;
        for (int i = 0; i < n; ++i) {
            if (nums[i] <= mid) {
                cnt++;
            }
        }
        if (cnt <= mid) {
            l = mid + 1;
        } else {
            r = mid - 1;
            ans = mid;
        }
    }
    return ans;
}


// loop
public int findDuplicate(int[] nums) {
    int slow = 0;
    int fast = 0;
    slow = nums[slow];
    fast = nums[nums[fast]];
    while(slow != fast){
        slow = nums[slow];
        fast = nums[nums[fast]];
    }
    int pre1 = 0;
    int pre2 = slow;
    while(pre1 != pre2){
        pre1 = nums[pre1];
        pre2 = nums[pre2];
    }
    return pre1;
}



"""











































