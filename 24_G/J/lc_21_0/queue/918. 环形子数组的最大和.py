# 918. 环形子数组的最大和

def maxSubarraySumCircular(self, A):
    total, maxSum, curMax, minSum, curMin = 0, A[0], 0, A[0], 0
    for a in A:
        curMax = max(curMax + a, a)
        maxSum = max(maxSum, curMax)
        curMin = min(curMin + a, a)
        minSum = min(minSum, curMin)
        total += a
    return max(maxSum, total - minSum) if maxSum > 0 else maxSum




def maxSubarraySumCircular(self, A):
    N = len(A)

    ans = cur = None
    for x in A:
        cur = x + max(cur, 0)
        ans = max(ans, cur)

    # ans is the answer for 1-interval subarrays.
    # Now, let's consider all 2-interval subarrays.
    # For each i, we want to know
    # the maximum of sum(A[j:]) with j >= i+2

    # rightsums[i] = sum(A[i:])
    rightsums = [None] * N
    rightsums[-1] = A[-1]
    for i in xrange(N-2, -1, -1):
        rightsums[i] = rightsums[i+1] + A[i]

    # maxright[i] = max_{j >= i} rightsums[j]
    maxright = [None] * N
    maxright[-1] = rightsums[-1]
    for i in xrange(N-2, -1, -1):
        maxright[i] = max(maxright[i+1], rightsums[i])

    leftsum = 0
    for i in xrange(N-2):
        leftsum += A[i]
        ans = max(ans, leftsum + maxright[i+2])
    return ans




"""
public int maxSubarraySumCircular(int[] A) {
    int N = A.length;

    int ans = A[0], cur = A[0];
    for (int i = 1; i < N; ++i) {
        cur = A[i] + Math.max(cur, 0);
        ans = Math.max(ans, cur);
    }

    // ans is the answer for 1-interval subarrays.
    // Now, let's consider all 2-interval subarrays.
    // For each i, we want to know
    // the maximum of sum(A[j:]) with j >= i+2

    // rightsums[i] = A[i] + A[i+1] + ... + A[N-1]
    int[] rightsums = new int[N];
    rightsums[N-1] = A[N-1];
    for (int i = N-2; i >= 0; --i)
        rightsums[i] = rightsums[i+1] + A[i];

    // maxright[i] = max_{j >= i} rightsums[j]
    int[] maxright = new int[N];
    maxright[N-1] = A[N-1];
    for (int i = N-2; i >= 0; --i)
        maxright[i] = Math.max(maxright[i+1], rightsums[i]);

    int leftsum = 0;
    for (int i = 0; i < N-2; ++i) {
        leftsum += A[i];
        ans = Math.max(ans, leftsum + maxright[i+2]);
    }

    return ans;
}



"""



def maxSubarraySumCircular(self, A):
    N = len(A)

    # Compute P[j] = sum(B[:j]) for the fixed array B = A+A
    P = [0]
    for _ in xrange(2):
        for x in A:
            P.append(P[-1] + x)

    # Want largest P[j] - P[i] with 1 <= j-i <= N
    # For each j, want smallest P[i] with i >= j-N
    ans = A[0]
    deque = collections.deque([0]) # i's, increasing by P[i]
    for j in xrange(1, len(P)):
        # If the smallest i is too small, remove it.
        if deque[0] < j-N:
            deque.popleft()

        # The optimal i is deque[0], for cand. answer P[j] - P[i].
        ans = max(ans, P[j] - P[deque[0]])

        # Remove any i1's with P[i2] <= P[i1].
        while deque and P[j] <= P[deque[-1]]:
            deque.pop()

        deque.append(j)

    return ans


"""
public int maxSubarraySumCircular(int[] A) {
    int N = A.length;

    // Compute P[j] = B[0] + B[1] + ... + B[j-1]
    // for fixed array B = A+A
    int[] P = new int[2*N+1];
    for (int i = 0; i < 2*N; ++i)
        P[i+1] = P[i] + A[i % N];

    // Want largest P[j] - P[i] with 1 <= j-i <= N
    // For each j, want smallest P[i] with i >= j-N
    int ans = A[0];
    // deque: i's, increasing by P[i]
    Deque<Integer> deque = new ArrayDeque();
    deque.offer(0);

    for (int j = 1; j <= 2*N; ++j) {
        // If the smallest i is too small, remove it.
        if (deque.peekFirst() < j-N)
            deque.pollFirst();

        // The optimal i is deque[0], for cand. answer P[j] - P[i].
        ans = Math.max(ans, P[j] - P[deque.peekFirst()]);

        // Remove any i1's with P[i2] <= P[i1].
        while (!deque.isEmpty() && P[j] <= P[deque.peekLast()])
            deque.pollLast();

        deque.offerLast(j);
    }

    return ans;
}

"""




# python3
class Solution:
    def maxSubarraySumCircular(self, nums: List[int]) -> int:
        nlen = len(nums)
        if nlen == 1:return nums[0]
        dp1 = []
        dp1.append(nums[0])
        dp2 = []
        dp2.append(nums[0])
        tmp_sum = nums[0]
        # 最大和 = max(总和-最小和,最大和)
        # 两种情况，1 不带环形最大和
        # 2.带环形最大和 = 总和 - 最小和
        # 若最大和为负数，则直接返回
        # 返回最大的
        for i in range(1,nlen):
            dp1.append(max(dp1[-1]+nums[i],nums[i]))
            dp2.append(min(dp2[-1]+nums[i],nums[i]))
            tmp_sum += nums[i]
        maxVal = max(dp1)
        minVal = min(dp2)
        if maxVal < 0:
            return maxVal
        return max(maxVal,tmp_sum-minVal)

# python3 简化版
class Solution:
    def maxSubarraySumCircular(self, nums: List[int]) -> int:
        nlen = len(nums)
        if nlen == 1:return nums[0]
        if nlen == 2:return max(nums[0]+nums[1],nums[1])
        # 两种情况，1不带环形(直接求最大和) 2 带环形(总和-最小和)
        maxval,tmp_sum,cur_max,minval,cur_min = nums[0],0,0,nums[0],0
        for i in range(nlen):
            tmp_sum += nums[i]
            cur_max = max(cur_max+nums[i],nums[i])
            maxval = max(cur_max,maxval)
            cur_min = min(cur_min+nums[i],nums[i])
            minval = min(cur_min,minval)
        if maxval < 0:
            return maxval
        return max(maxval,tmp_sum-minval)





