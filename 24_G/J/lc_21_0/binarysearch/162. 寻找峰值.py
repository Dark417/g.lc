# 162. 寻找峰值

"""
public int findPeakElement(int[] nums) {
    int left = 0, right = nums.length - 1;
    for (; left < right; ) {
        int mid = left + (right - left) / 2;
        if (nums[mid] > nums[mid + 1]) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    return left;
}



public int findPeakElement(int[] nums) {
    int n = nums.length;
    int l = 0, r = n - 1;
    while (l < r) {
        int mid = l + r >> 1;
        if (nums[mid] > nums[mid + 1]) r = mid;
        else l = mid + 1;
    }
    return r;
}


 public int findPeakElement(int[] nums) {
    int n = nums.length;
    if (n == 1) return 0;
    int l = 0, r = n - 1;
    while (l < r) {
        int mid = l + r + 1 >> 1;
        if (nums[mid] > nums[mid - 1]) l = mid;
        else r = mid - 1;
    }
    return r; //l 
}




"""

def findPeakElement(self, nums: List[int]) -> int:
    n = len(nums)

    # 辅助函数，输入下标 i，返回 nums[i] 的值
    # 方便处理 nums[-1] 以及 nums[n] 的边界情况
    def get(i: int) -> int:
        if i == -1 or i == n:
            return float('-inf')
        return nums[i]
    
    left, right, ans = 0, n - 1, -1
    while left <= right:
        mid = (left + right) // 2
        if get(mid - 1) < get(mid) > get(mid + 1):
            ans = mid
            break
        if get(mid) < get(mid + 1):
            left = mid + 1
        else:
            right = mid - 1
    
    return ans


def findPeakElement(self, nums: List[int]) -> int:
    def get(i):
        if i == -1 or i == len(nums):
            return -float("inf")
        else:
            return nums[i]

    n = len(nums)
    l, r = 0, n - 1
    while l <= r:
        mid = l + (r - l) // 2
        if get(mid-1) < get(mid) > get(mid+1):
            return mid
        elif get(mid-1) < get(mid):
            l = mid + 1
        else:
            r = mid - 1
    return mid

"""
public int findPeakElement(int[] nums) {
    int n = nums.length;
    int left = 0, right = n - 1, ans = -1;
    while (left <= right) {
        int mid = (left + right) / 2;
        if (compare(nums, mid - 1, mid) < 0 && compare(nums, mid, mid + 1) > 0) {
            ans = mid;
            break;
        }
        if (compare(nums, mid, mid + 1) < 0) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return ans;
}

// 辅助函数，输入下标 i，返回一个二元组 (0/1, nums[i])
// 方便处理 nums[-1] 以及 nums[n] 的边界情况
public int[] get(int[] nums, int idx) {
    if (idx == -1 || idx == nums.length) {
        return new int[]{0, 0};
    }
    return new int[]{1, nums[idx]};
}

public int compare(int[] nums, int idx1, int idx2) {
    int[] num1 = get(nums, idx1);
    int[] num2 = get(nums, idx2);
    if (num1[0] != num2[0]) {
        return num1[0] > num2[0] ? 1 : -1;
    }
    if (num1[1] == num2[1]) {
        return 0;
    }
    return num1[1] > num2[1] ? 1 : -1;
}



"""



def findPeakElement(self, nums: List[int]) -> int:
    idx = 0
    for i in range(1, len(nums)):
        if nums[i] > nums[idx]:
            idx = i
    return idx


def findPeakElement(self, nums: List[int]) -> int:
    n = len(nums)
    idx = random.randint(0, n - 1)

    # 辅助函数，输入下标 i，返回 nums[i] 的值
    # 方便处理 nums[-1] 以及 nums[n] 的边界情况
    def get(i: int) -> int:
        if i == -1 or i == n:
            return float('-inf')
        return nums[i]
    
    while not (get(idx - 1) < get(idx) > get(idx + 1)):
        if get(idx) < get(idx + 1):
            idx += 1
        else:
            idx -= 1
    
    return idx




































