# 724. 寻找数组的中心下标

# 1991. 找到数组的中间位置


# 剑指 Offer II 012. 左右两边子数组的和



def pivotIndex(self, nums: List[int]) -> int:
    presum = [0] * (len(nums) + 1)
    for i in range(len(nums)):
        presum[i + 1] = presum[i] + nums[i]
    
    for i in range(len(nums)):
        if i == 0:
            if presum[len(nums)] - presum[1] == 0:
                return 0
        elif i == len(nums) - 1:
            if presum[len(nums)-1] - presum[0] == 0:
                return len(nums) - 1
        elif presum[i] - presum[0] == presum[len(nums)] - presum[i+1]:
            return i
    return -1


def pivotIndex(self, nums: List[int]) -> int:
    sm = sum(nums)
    smcur = 0
    for i in range(len(nums)):
        if smcur * 2 + nums[i] == sm:
            return i
        smcur += nums[i]
    return -1



"""
class Solution {
public:
    int pivotIndex(vector<int>& nums) {
        int left = 0; 
        int right = accumulate(nums.begin(), nums.end(),0);
        for (int i = 0; i < nums.size(); ++i)
        {
            right -= nums[i];
            if (left == right)
                return i;
            left += nums[i];
        }
        return -1;
    }
};
"""


















