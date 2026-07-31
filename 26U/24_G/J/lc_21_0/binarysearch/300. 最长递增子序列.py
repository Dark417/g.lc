# 300. 最长递增子序列


def lengthOfLIS(self, nums: List[int]) -> int:
    if not nums:
        return 0
    dp = []
    for i in range(len(nums)):
        dp.append(1)
        for j in range(i):
            if nums[i] > nums[j]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)




def lengthOfLIS(self, nums: List[int]) -> int:
    d = []
    for n in nums:
        if not d or n > d[-1]:
            d.append(n)
        else:
            l, r = 0, len(d) - 1
            loc = r
            while l <= r:
                mid = (l + r) // 2
                if d[mid] >= n:
                    loc = mid
                    r = mid - 1
                else:
                    l = mid + 1
            d[loc] = n
    return len(d)






"""
public int lengthOfLIS(int[] nums) {
    int len = 1, n = nums.length;
    if (n == 0) {
        return 0;
    }
    int[] d = new int[n + 1];
    d[len] = nums[0];
    for (int i = 1; i < n; ++i) {
        if (nums[i] > d[len]) {
            d[++len] = nums[i];
        } else {
            int l = 1, r = len, pos = 0; // 如果找不到说明所有的数都比 nums[i] 大，此时要更新 d[1]，所以这里将 pos 设为 0
            while (l <= r) {
                int mid = (l + r) >> 1;
                if (d[mid] < nums[i]) {
                    pos = mid;
                    l = mid + 1;
                } else {
                    r = mid - 1;
                }
            }
            d[pos + 1] = nums[i];
        }
    }
    return len;
}

"""


# luffy
def lengthOfLIS(self, nums: [int]) -> int:
    tails, res = [0] * len(nums), 0
    for num in nums:
        i, j = 0, res
        while i < j:
            m = (i + j) // 2
            if tails[m] < num: i = m + 1 # 如果要求非严格递增，将此行 '<' 改为 '<=' 即可。
            else: j = m
        tails[i] = num
        if j == res: res += 1
    return res




def lengthOfLIS(self, nums: List[int]) -> int:
    res = 0
    dp = [1] * len(nums)
    for i in range(1, len(nums)):
        for j in range(i):
            if nums[i] > nums[j]:
                dp[i] = max(dp[j] + 1, dp[i])
        # res = max(res, dp[i])
    return max(dp)


def lengthOfLIS(self, nums: List[int]) -> int:
    res = 0
    dp = [1] * len(nums)
    
    for i in range(1, len(nums)):
        curmax = 1

        for j in range(i):
            if nums[i] > nums[j]:
                curmax = max(dp[j], curmax)
                dp[i] = curmax + 1
    return max(dp)


"""
public int lengthOfLIS(int[] nums) {
    if (nums.length == 0) {
        return 0;
    }
    int[] dp = new int[nums.length];
    dp[0] = 1;
    int maxans = 1;
    for (int i = 1; i < nums.length; i++) {
        dp[i] = 1;
        for (int j = 0; j < i; j++) {
            if (nums[i] > nums[j]) {
                dp[i] = Math.max(dp[i], dp[j] + 1);
            }
        }
        maxans = Math.max(maxans, dp[i]);
    }
    return maxans;
}



"""



def lengthOfLIS(self, nums: List[int]) -> int:
    if not nums:
        return 0
    dp = []
    for i in range(len(nums)):
        dp.append(1)
        for j in range(i):
            if nums[i] > nums[j]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)












































