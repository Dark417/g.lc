# 540. 有序数组中的单一元素

def singleNonDuplicate(self, nums: List[int]) -> int:
    l, r = 0, len(nums) - 1
    while l < r:
        mid = l + (r - l) // 2
        if mid%2 and nums[mid] == nums[mid-1] or not mid%2 and nums[mid] == nums[mid+1]:
            l = mid + 1
        else:
            r = mid
    return nums[l]


# mid是偶数时, mid+1=mid⊕1
# mid是奇数时, mid−1=mid⊕1

def singleNonDuplicate(self, nums: List[int]) -> int:
    low, high = 0, len(nums) - 1
    while low < high:
        mid = (low + high) // 2
        if nums[mid] == nums[mid ^ 1]:
            low = mid + 1
        else:
            high = mid
    return nums[low]


"""
public int singleNonDuplicate(int[] nums) {
    int low = 0, high = nums.length - 1;
    while (low < high) {
        int mid = (high - low) / 2 + low;
        if (nums[mid] == nums[mid ^ 1]) {
            low = mid + 1;
        } else {
            high = mid;
        }
    }
    return nums[low];
}


public int singleNonDuplicate(int[] nums) {
    int ans = 0;
    for (int i : nums) ans ^= i;
    return ans;
}


public int singleNonDuplicate(int[] nums) {
    int n = nums.length;
    for (int i = 0; i < n - 1; i += 2) {
        if (nums[i] != nums[i + 1]) return nums[i];
    }
    return nums[n - 1];
}




"""

























