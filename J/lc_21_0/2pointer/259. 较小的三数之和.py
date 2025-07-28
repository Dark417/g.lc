# 259. 较小的三数之和

def threeSumSmaller(self, nums: List[int], target: int) -> int:
    if len(nums) < 3:  # 处理边界条件
        return 0
    nums.sort()
    ans = 0
    for i in range(len(nums) - 2):  # 注意i,j,k三个指针不能重合
        left = i + 1
        right = len(nums) - 1
        while left < right:
            # 如果left和right之和小于target-nums[i]，left右移
            if nums[left] + nums[right] < target - nums[i]:
                ans += right - left
                left += 1 
            # 如果left和right之和大于target-nums[i]，right左移
            else:
                right -= 1
    return ans



def threeSumSmaller(self, nums: List[int], target: int) -> int:
    n,res=len(nums),0
    nums.sort()
    for i,j in itertools.combinations(range(n),2):
        res+=max(0,bisect_left(nums,target-nums[i]-nums[j])-j-1)
    return res





"""
public int threeSumSmaller(int[] nums, int target) {
    Arrays.sort(nums);
    int sum = 0;
    for (int i = 0; i < nums.length - 2; i++) {
        sum += twoSumSmaller(nums, i + 1, target - nums[i]);
    }
    return sum;
}

private int twoSumSmaller(int[] nums, int startIndex, int target) {
    int sum = 0;
    for (int i = startIndex; i < nums.length - 1; i++) {
        int j = binarySearch(nums, i, target - nums[i]);
        sum += j - i;
    }
    return sum;
}

private int binarySearch(int[] nums, int startIndex, int target) {
    int left = startIndex;
    int right = nums.length - 1;
    while (left < right) {
        int mid = (left + right + 1) / 2;
        if (nums[mid] < target) {
            left = mid;
        } else {
            right = mid - 1;
        }
    }
    return left;
}



public int threeSumSmaller(int[] nums, int target) {
    Arrays.sort(nums);
    int sum = 0;
    for (int i = 0; i < nums.length - 2; i++) {
        sum += twoSumSmaller(nums, i + 1, target - nums[i]);
    }
    return sum;
}

private int twoSumSmaller(int[] nums, int startIndex, int target) {
    int sum = 0;
    int left = startIndex;
    int right = nums.length - 1;
    while (left < right) {
        if (nums[left] + nums[right] < target) {
            sum += right - left;
            left++;
        } else {
            right--;
        }
    }
    return sum;
}


"""












