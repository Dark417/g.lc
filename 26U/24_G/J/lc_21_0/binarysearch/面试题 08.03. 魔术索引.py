# 面试题 08.03. 魔术索引

# 官方题解这所谓的二分递归，实际上还是从左到右把数组遍历了一遍吧，二分每次能排除一半元素，但这个实际上先搜左边，左边搜不到搜右边，感觉还是在做遍历，那倒不如在直接遍历上做一个跳跃性的优化。



return next(iter(i for i,num in enumerate(nums) if i==num),-1)

def findMagicIndex(self, nums: List[int]) -> int:
    i=0
    while i < len(nums):
        if i==nums[i]:
            return i
        if i<nums[i]:
            i=nums[i]
        else:
            i+=1
    return -1


"""

public int findMagicIndex(int[] nums) {
        return getAnswer(nums, 0, nums.length - 1);
    }

public int getAnswer(int[] nums, int left, int right) {
    if (left > right) {
        return -1;
    }
    int mid = (right - left) / 2 + left;
    int leftAnswer = getAnswer(nums, left, mid - 1);
    if (leftAnswer != -1) {
        return leftAnswer;
    } else if (nums[mid] == mid) {
        return mid;
    }
    return getAnswer(nums, mid + 1, right);
}



public int findMagicIndex(int[] nums) {
        return helper(nums, 0, nums.length - 1);
    }

    public int helper(int[] nums, int lo, int hi) {
        if (lo > hi)
            return -1;
        int mid = lo + (hi - lo) / 2;
        int res = helper(nums, lo, mid - 1);
        if (res != -1) {
            return res;
        } else if (nums[mid] == mid) {
            return mid;
        } else {
            return helper(nums, mid + 1, hi);
        }
    }



"""












































