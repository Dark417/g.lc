# 611. 有效三角形的个数

def triangleNumber(self, nums: List[int]) -> int:
    n = len(nums)
    nums.sort()
    ans = 0
    for i in range(n):
        for j in range(i + 1, n):
            left, right, k = j + 1, n - 1, j
            while left <= right:
                mid = (left + right) // 2
                if nums[mid] < nums[i] + nums[j]:
                    k = mid
                    left = mid + 1
                else:
                    right = mid - 1
            ans += k - j
    return ans


"""
public int triangleNumber(int[] nums) {
    int n = nums.length;
    Arrays.sort(nums);
    int ans = 0;
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            int left = j + 1, right = n - 1, k = j;
            while (left <= right) {
                int mid = (left + right) / 2;
                if (nums[mid] < nums[i] + nums[j]) {
                    k = mid;
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
            ans += k - j;
        }
    }
    return ans;
}

"""

def triangleNumber(self, nums: List[int]) -> int:
    n = len(nums)
    nums.sort()
    ans = 0
    for i in range(n):
        k = i
        for j in range(i + 1, n):
            while k + 1 < n and nums[k + 1] < nums[i] + nums[j]:
                k += 1
            ans += max(k - j, 0)
    return ans


def triangleNumber(self, nums: List[int]) -> int:
    res = 0
    nums.sort()
    n = len(nums)
    for i in range(n):
        k = i + 1
        for j in range(i+1, n):
            while k < n and nums[k] < nums[i] + nums[j]:
                k += 1
            res += max(k - 1 - j, 0)
    return res
        
"""
public int triangleNumber(int[] nums) {
    int n = nums.length;
    Arrays.sort(nums);
    int ans = 0;
    for (int i = 0; i < n; ++i) {
        int k = i;
        for (int j = i + 1; j < n; ++j) {
            while (k + 1 < n && nums[k + 1] < nums[i] + nums[j]) {
                ++k;
            }
            ans += Math.max(k - j, 0);
        }
    }
    return ans;
}


"""


def triangleNumber(self, nums: List[int]) -> int:
    n = len(nums)
    ans = 0
    nums.sort()
    for i in range(n - 2):
        if nums[i] == 0: continue
        k = i + 2
        for j in range(i + 1, n - 1):
            while k < n and nums[i] + nums[j] > nums[k]:
                k += 1
            ans += k - j - 1
    return ans


def triangleNumber(self, s: List[int]) -> int:
    nums.sort()
    res = 0 
    for k in range(len(nums)):
        i, j = 0, k - 1
        while i < j:
            if nums[i] + nums[j] > nums[k]:
                res += j - i
                j -= 1
            else:
                i += 1
    return res



def triangleNumber(self, num: List[int]) -> int:
    num=sorted(num,reverse=True)
    ans=0
    if len(num)>2:
        for i in range(len(num)-2):
            left = i+1
            right = len(num)-1
            while left<right:
                if num[left]+num[right]>num[i]:
                    ans+=(right-left)
                    left+=1
                else:
                    right-=1
    return ans if len(num)>2 else 0



"""
binary search, k from where left last time
int binarySearch(int nums[], int l, int r, int x) {
    while (r >= l && r < nums.length) {
        int mid = (l + r) / 2;
        if (nums[mid] >= x)
            r = mid - 1;
        else
            l = mid + 1;
    }
    return l;
}
public int triangleNumber(int[] nums) {
    int count = 0;
    Arrays.sort(nums);
    for (int i = 0; i < nums.length - 2; i++) {
        int k = i + 2;
        for (int j = i + 1; j < nums.length - 1 && nums[i] != 0; j++) {
            k = binarySearch(nums, k, nums.length - 1, nums[i] + nums[j]);
            count += k - j - 1;
        }
    }
    return count;
}


linear scan

public int triangleNumber(int[] nums) {
        int count = 0;
        Arrays.sort(nums);
        for (int i = 0; i < nums.length - 2; i++) {
            int k = i + 2;
            for (int j = i + 1; j < nums.length - 1 && nums[i] != 0; j++) {
                while (k < nums.length && nums[i] + nums[j] > nums[k])
                    k++;
                count += k - j - 1;
            }
        }
        return count;
    }
}

"""


















