"""
170.53. Maximum Subarray
最大子序和

Given an integer array nums, find the contiguous subarray (containing at least one number) 
which has the largest sum and return its sum.

Example:

Input: [-2,1,-3,4,-1,2,1,-5,4],
Output: 6
Explanation: [4,-1,2,1] has the largest sum = 6.
Follow up:

If you have figured out the O(n) solution, try coding another solution using the divide 
and conquer approach, which is more subtle.


https://leetcode-cn.com/problems/maximum-subarray/solution/zui-da-zi-xu-he-by-leetcode-solution/

"""








def maxSubArray(self, nums: List[int]) -> int:
    #res = -float('inf')
    res = 0
    for i in range(len(nums)-1):
        for j+1 in range(i+1, len(nums)):
            res = max(res, sum(nums[i,j]))
    return res



    for i in range(1, len(nums)):
        if nums[i-1] > 0:
            nums[i] += nums[i-1]
    return max(nums)


def maxSubArray(self, nums: List[int]) -> int:
    for i in range(1, len(nums)):
        nums[i] += max(nums[i - 1], 0)
    return max(nums)






def maxSubArray(self, nums: List[int]) -> int:
    if not nums: return 0
    mx = nums[0]
    for i in range(1, len(nums)):
        if nums[i-1] > 0:
            nums[i] += nums[i-1]
        mx = max(mx, nums[i])
    return mx





# greedy
def maxSubArray(self, nums: List[int]) -> int:
    s, mx = 0, -float("inf")
    for i in nums:
        if s >= 0:
            s += i
        else:
            s = i
        mx = max(mx, s)
    return mx



def maxSubArray(self, nums: List[int]) -> int:
    s, mn, res = 0, 0, nums[0]
    for i in range(len(nums)):
        s += nums[i]
        if s - mn > res:
            res = s - mn
        if s < mn:
            mn = s
    return res



def maxSubArray(self, nums):
    if not nums: return None
    max_sum = float('-inf')
    curr_sum = 0  # Optimal sum ending with the current number
    for n in nums:
        curr_sum = max(n, curr_sum + n)
        max_sum = max(max_sum, curr_sum)
    return max_sum



def maxSubArray(self, A):
    current = 0
    result = A[0]
    for i in A:
        current += i
        result = max(current,result)
        current = max(0,current)
    return result



"""
int maxSubArray(int A[], int n) {
    int sum = 0, min = 0, res = A[0];
    for(int i = 0; i < n; i++) {
        sum += A[i];
        if(sum - min > res) res = sum - min;
        if(sum < min) min = sum;
    }
    return res;
}

"""

"""
struct val {
    int l, m, r, s;
    val(int l, int m, int r, int s):l(l), m(m), r(r), s(s){}
};

class Solution {
public:
    val dac(int A[], int n) {
        if(n == 1) return val(A[0], A[0], A[0], A[0]);
        val v1 = dac(A, n / 2), v2 = dac(A + n / 2, n - n / 2);
        int l, m, r, s;
        l = max(v1.l, v1.s + v2.l);
        m = max(v1.r + v2.l, max(v1.m, v2.m));
        r = max(v2.r, v1.r + v2.s);
        s = v1.s + v2.s;
        return val(l, m, r, s);
    }
    int maxSubArray(int A[], int n) {
        val v = dac(A, n);
        return v.m;
    }
};
"""













# dp
def maxSubArray(self, A):
    curSum = maxSum = A[0]
    for num in A[1:]:
        curSum = max(num, curSum + num)
        maxSum = max(maxSum, curSum)
    return maxSum






def maxSubArray(self, nums: List[int]) -> int:
    tmp = nums[0]
    max_ = tmp
    n = len(nums)
    for i in range(1,n):
        # 当当前序列加上此时的元素的值大于tmp的值，说明最大序列和可能出现在后续序列中，记录此时的最大值
        if tmp + nums[i]>nums[i]:
            max_ = max(max_, tmp+nums[i])
            tmp = tmp + nums[i]
        else:
        #当tmp(当前和)小于下一个元素时，当前最长序列到此为止。以该元素为起点继续找最大子序列,
        # 并记录此时的最大值
            max_ = max(max_, tmp, tmp+nums[i], nums[i])
            tmp = nums[i]
    return max_



def maxSubArray(self, nums):
    max_so_far = curr_so_far = -float('inf')
    for i in xrange(len(nums)):
        curr_so_far += nums[i] # Add curr number
        curr_so_far = max(curr_so_far, nums[i]) # Check if should abandon accumulated value so far if it's a burden due to negative value accumulated
        max_so_far = max(max_so_far, curr_so_far) # Update answer
        
    return max_so_far





def maxSubArray(self, nums: List[int]) -> int:
    n = len(nums)
    #递归终止条件
    if n == 1:
        return nums[0]
    else:
        #递归计算左半边最大子序和
        max_left = self.maxSubArray(nums[0:len(nums) // 2])
        #递归计算右半边最大子序和
        max_right = self.maxSubArray(nums[len(nums) // 2:len(nums)])
    
    #计算中间的最大子序和，从右到左计算左边的最大子序和，从左到右计算右边的最大子序和，再相加
    max_l = nums[len(nums) // 2 - 1]
    tmp = 0
    for i in range(len(nums) // 2 - 1, -1, -1):
        tmp += nums[i]
        max_l = max(tmp, max_l)
    max_r = nums[len(nums) // 2]
    tmp = 0
    for i in range(len(nums) // 2, len(nums)):
        tmp += nums[i]
        max_r = max(tmp, max_r)
    #返回三个中的最大值
    return max(max_right,max_left,max_l+max_r)



def maxSubArray(self, nums: List[int]) -> int:
    def dnc(nums, l, r):
        if not nums or r < l:
            return 0, 0, 0, 0
        if l == r:
            return nums[l], nums[l], nums[l], nums[l]
        m = (l + r) // 2
        ll, lr, lm, ls = dnc(nums, l, m)  # left max, right max, mid max, sum of left
        rl, rr, rm, rs = dnc(nums, m+1, r)  # left max, right max, mid max, sum of right
        ml = max(ll, ls + rl)
        mr = max(rr, rs + lr)
        mm = max(lc, rm, lr + rl)
        ms = ls + rs
        return ml, mr, mm, ms  # left max, right max, mid max, sum of merge
    
    return dnc(nums, 0, len(nums)-1)[2]



























































