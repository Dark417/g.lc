# 209. 长度最小的子数组


# 2p
def minSubArrayLen(self, s: int, nums: List[int]) -> int:
    if not nums:
        return 0
    
    n = len(nums)
    ans = n + 1
    start, end = 0, 0
    total = 0
    while end < n:
        total += nums[end]
        while total >= s:
            ans = min(ans, end - start + 1)
            total -= nums[start]
            start += 1
        end += 1
    
    return 0 if ans == n + 1 else ans


"""
public int minSubArrayLen(int s, int[] nums) {
    int n = nums.length;
    if (n == 0) {
        return 0;
    }
    int ans = Integer.MAX_VALUE;
    int start = 0, end = 0;
    int sum = 0;
    while (end < n) {
        sum += nums[end];
        while (sum >= s) {
            ans = Math.min(ans, end - start + 1);
            sum -= nums[start];
            start++;
        }
        end++;
    }
    return ans == Integer.MAX_VALUE ? 0 : ans;
}

"""



# bs
def minSubArrayLen(self, s: int, nums: List[int]) -> int:
    if not nums:
        return 0
    
    n = len(nums)
    ans = n + 1
    sums = [0]
    for i in range(n):
        sums.append(sums[-1] + nums[i])
    
    for i in range(1, n + 1):
        target = s + sums[i - 1]
        bound = bisect.bisect_left(sums, target)
        if bound != len(sums):
            ans = min(ans, bound - (i - 1))
    
    return 0 if ans == n + 1 else ans


"""
public int minSubArrayLen(int s, int[] nums) {
    int n = nums.length;
    if (n == 0) {
        return 0;
    }
    int ans = Integer.MAX_VALUE;
    int[] sums = new int[n + 1]; 
    // 为了方便计算，令 size = n + 1 
    // sums[0] = 0 意味着前 0 个元素的前缀和为 0
    // sums[1] = A[0] 前 1 个元素的前缀和为 A[0]
    // 以此类推
    for (int i = 1; i <= n; i++) {
        sums[i] = sums[i - 1] + nums[i - 1];
    }
    for (int i = 1; i <= n; i++) {
        int target = s + sums[i - 1];
        int bound = Arrays.binarySearch(sums, target);
        if (bound < 0) {
            bound = -bound - 1;
        }
        if (bound <= n) {
            ans = Math.min(ans, bound - (i - 1));
        }
    }
    return ans == Integer.MAX_VALUE ? 0 : ans;
}


"""



# brute
def minSubArrayLen(self, s: int, nums: List[int]) -> int:
    if not nums:
        return 0
    
    n = len(nums)
    ans = n + 1
    for i in range(n):
        total = 0
        for j in range(i, n):
            total += nums[j]
            if total >= s:
                ans = min(ans, j - i + 1)
                break
    
    return 0 if ans == n + 1 else ans


"""
public int minSubArrayLen(int s, int[] nums) {
    int n = nums.length;
    if (n == 0) {
        return 0;
    }
    int ans = Integer.MAX_VALUE;
    for (int i = 0; i < n; i++) {
        int sum = 0;
        for (int j = i; j < n; j++) {
            sum += nums[j];
            if (sum >= s) {
                ans = Math.min(ans, j - i + 1);
                break;
            }
        }
    }
    return ans == Integer.MAX_VALUE ? 0 : ans;
}


"""















