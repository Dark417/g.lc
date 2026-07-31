# 81. 搜索旋转排序数组 II



def search(self, nums, target):
    if not nums: return -1
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) / 2
        if nums[mid] == target:
            return True
        if nums[left] == nums[right]:
            left += 1
            continue
        if nums[mid] <= nums[right]:
            if target > nums[mid] and target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
        else:
            if target < nums[mid] and target >= nums[left]:
                right = mid - 1
            else:
                left = mid + 1
    return False



        


def search(self, nums: List[int], target: int) -> bool:
    if not nums:
        return False
    
    n = len(nums)
    if n == 1:
        return nums[0] == target
    
    l, r = 0, n - 1
    while l <= r:
        mid = (l + r) // 2
        if nums[mid] == target:
            return True
        if nums[l] == nums[mid] and nums[mid] == nums[r]:
            l += 1
            r -= 1
        elif nums[l] <= nums[mid]:
            if nums[l] <= target and target < nums[mid]:
                r = mid - 1
            else:
                l = mid + 1
        else:
            if nums[mid] < target and target <= nums[n - 1]:
                l = mid + 1
            else:
                r = mid - 1
    
    return False



"""
public boolean search(int[] nums, int target) {
    int n = nums.length;
    if (n == 0) {
        return false;
    }
    if (n == 1) {
        return nums[0] == target;
    }
    int l = 0, r = n - 1;
    while (l <= r) {
        int mid = (l + r) / 2;
        if (nums[mid] == target) {
            return true;
        }
        if (nums[l] == nums[mid] && nums[mid] == nums[r]) {
            ++l;
            --r;
        } else if (nums[l] <= nums[mid]) {
            if (nums[l] <= target && target < nums[mid]) {
                r = mid - 1;
            } else {
                l = mid + 1;
            }
        } else {
            if (nums[mid] < target && target <= nums[n - 1]) {
                l = mid + 1;
            } else {
                r = mid - 1;
            }
        }
    }
    return false;
}
"""






























