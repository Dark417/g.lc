# 4. 寻找两个正序数组的中位数


def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
    if len(nums1) > len(nums2):
        return self.findMedianSortedArrays(nums2, nums1)

    infinty = 2**40
    m, n = len(nums1), len(nums2)
    left, right = 0, m
    # median1：前一部分的最大值
    # median2：后一部分的最小值
    median1, median2 = 0, 0

    while left <= right:
        # 前一部分包含 nums1[0 .. i-1] 和 nums2[0 .. j-1]
        # // 后一部分包含 nums1[i .. m-1] 和 nums2[j .. n-1]
        i = (left + right) // 2
        j = (m + n + 1) // 2 - i

        # nums_im1, nums_i, nums_jm1, nums_j 分别表示 nums1[i-1], nums1[i], nums2[j-1], nums2[j]
        nums_im1 = (-infinty if i == 0 else nums1[i - 1])
        nums_i = (infinty if i == m else nums1[i])
        nums_jm1 = (-infinty if j == 0 else nums2[j - 1])
        nums_j = (infinty if j == n else nums2[j])

        if nums_im1 <= nums_j:
            median1, median2 = max(nums_im1, nums_jm1), min(nums_i, nums_j)
            left = i + 1
        else:
            right = i - 1

    return (median1 + median2) / 2 if (m + n) % 2 == 0 else median1


"""
public double findMedianSortedArrays(int[] nums1, int[] nums2) {
	if (nums1.length > nums2.length) {
		int[] temp = nums1;
		nums1 = nums2;
		nums2 = temp;
	}

	int m = nums1.length;
	int n = nums2.length;

	int totalLeft = (m + n + 1) // 2
	int left = 0;
	int right = m;

	while (left < right) {
		int i = left + (right - left + 1) / 2
		int j = totalLeft - i;

		if (nums1[i-i] > nums2[j]) {
			right = i - 1;
		} else {
			left = i;
		}
	}

	int i = left;
	int j = totalLeft - i;

	int nums1LeftMax = i == 0 ? Integer.MIN_VALUE : nums1[i-1];
	int nums1RightMin = i == m ? Integer.Max_VALUE : nums1[i];
	int nums2LeftMax = j == 0 ? Integer.MIN_VALUE : nums2[j-1];
	int nums2RightMin = j == n? Integer.MAX_VALUE : nums2[j];

	if (((m + n) % 2) == 1) {
		return Math.max(nums1.LeftMax, nums2.LeftMax);
	} else {
		return (double)((Math.max(nums1LeftMax, nums2LeftMax)+
		Math.min(nums1RightMin, nums2Rightmin)) / 2;
	}



}



public double findMedianSortedArrays(int[] nums1, int[] nums2) {
    if (nums1.length > nums2.length) {
        return findMedianSortedArrays(nums2, nums1);
    }

    int m = nums1.length;
    int n = nums2.length;
    int left = 0, right = m;
    // median1：前一部分的最大值
    // median2：后一部分的最小值
    int median1 = 0, median2 = 0;

    while (left <= right) {
        // 前一部分包含 nums1[0 .. i-1] 和 nums2[0 .. j-1]
        // 后一部分包含 nums1[i .. m-1] 和 nums2[j .. n-1]
        int i = (left + right) / 2;
        int j = (m + n + 1) / 2 - i;

        // nums_im1, nums_i, nums_jm1, nums_j 分别表示 nums1[i-1], nums1[i], nums2[j-1], nums2[j]
        int nums_im1 = (i == 0 ? Integer.MIN_VALUE : nums1[i - 1]);
        int nums_i = (i == m ? Integer.MAX_VALUE : nums1[i]);
        int nums_jm1 = (j == 0 ? Integer.MIN_VALUE : nums2[j - 1]);
        int nums_j = (j == n ? Integer.MAX_VALUE : nums2[j]);

        if (nums_im1 <= nums_j) {
            median1 = Math.max(nums_im1, nums_jm1);
            median2 = Math.min(nums_i, nums_j);
            left = i + 1;
        } else {
            right = i - 1;
        }
    }

    return (m + n) % 2 == 0 ? (median1 + median2) / 2.0 : median1;
}


"""

# powcai
def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
    n1 = len(nums1)
    n2 = len(nums2)
    if n1 > n2:
        return self.findMedianSortedArrays(nums2,nums1)
    k = (n1 + n2 + 1)//2
    left = 0
    right = n1
    while left< right :
        m1 = left +(right - left)//2
        m2 = k - m1
        if nums1[m1] < nums2[m2-1]:
            left = m1 + 1
        else:
            right = m1
    m1 = left
    m2 = k - m1 
    c1 = max(nums1[m1-1] if m1 > 0 else float("-inf"), nums2[m2-1] if m2 > 0 else float("-inf") )
    if (n1 + n2) % 2 == 1:
        return c1
    c2 = min(nums1[m1] if m1 < n1 else float("inf"), nums2[m2] if m2 <n2 else float("inf"))
    return (c1 + c2) / 2





def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
    def getKthElement(k):
        """
        - 主要思路：要找到第 k (k>1) 小的元素，那么就取 pivot1 = nums1[k/2-1] 和 pivot2 = nums2[k/2-1] 进行比较
        - 这里的 "/" 表示整除
        - nums1 中小于等于 pivot1 的元素有 nums1[0 .. k/2-2] 共计 k/2-1 个
        - nums2 中小于等于 pivot2 的元素有 nums2[0 .. k/2-2] 共计 k/2-1 个
        - 取 pivot = min(pivot1, pivot2)，两个数组中小于等于 pivot 的元素共计不会超过 (k/2-1) + (k/2-1) <= k-2 个
        - 这样 pivot 本身最大也只能是第 k-1 小的元素
        - 如果 pivot = pivot1，那么 nums1[0 .. k/2-1] 都不可能是第 k 小的元素。把这些元素全部 "删除"，剩下的作为新的 nums1 数组
        - 如果 pivot = pivot2，那么 nums2[0 .. k/2-1] 都不可能是第 k 小的元素。把这些元素全部 "删除"，剩下的作为新的 nums2 数组
        - 由于我们 "删除" 了一些元素（这些元素都比第 k 小的元素要小），因此需要修改 k 的值，减去删除的数的个数
        """
        
        index1, index2 = 0, 0
        while True:
            # 特殊情况
            if index1 == m:
                return nums2[index2 + k - 1]
            if index2 == n:
                return nums1[index1 + k - 1]
            if k == 1:
                return min(nums1[index1], nums2[index2])

            # 正常情况
            newIndex1 = min(index1 + k // 2 - 1, m - 1)
            newIndex2 = min(index2 + k // 2 - 1, n - 1)
            pivot1, pivot2 = nums1[newIndex1], nums2[newIndex2]
            if pivot1 <= pivot2:
                k -= newIndex1 - index1 + 1
                index1 = newIndex1 + 1
            else:
                k -= newIndex2 - index2 + 1
                index2 = newIndex2 + 1
    
    m, n = len(nums1), len(nums2)
    totalLength = m + n
    if totalLength % 2 == 1:
        return getKthElement((totalLength + 1) // 2)
    else:
        return (getKthElement(totalLength // 2) + getKthElement(totalLength // 2 + 1)) / 2




"""
public double findMedianSortedArrays(int[] nums1, int[] nums2) {
    int length1 = nums1.length, length2 = nums2.length;
    int totalLength = length1 + length2;
    if (totalLength % 2 == 1) {
        int midIndex = totalLength / 2;
        double median = getKthElement(nums1, nums2, midIndex + 1);
        return median;
    } else {
        int midIndex1 = totalLength / 2 - 1, midIndex2 = totalLength / 2;
        double median = (getKthElement(nums1, nums2, midIndex1 + 1) + getKthElement(nums1, nums2, midIndex2 + 1)) / 2.0;
        return median;
    }
}

public int getKthElement(int[] nums1, int[] nums2, int k) {
    /* 主要思路：要找到第 k (k>1) 小的元素，那么就取 pivot1 = nums1[k/2-1] 和 pivot2 = nums2[k/2-1] 进行比较
     * 这里的 "/" 表示整除
     * nums1 中小于等于 pivot1 的元素有 nums1[0 .. k/2-2] 共计 k/2-1 个
     * nums2 中小于等于 pivot2 的元素有 nums2[0 .. k/2-2] 共计 k/2-1 个
     * 取 pivot = min(pivot1, pivot2)，两个数组中小于等于 pivot 的元素共计不会超过 (k/2-1) + (k/2-1) <= k-2 个
     * 这样 pivot 本身最大也只能是第 k-1 小的元素
     * 如果 pivot = pivot1，那么 nums1[0 .. k/2-1] 都不可能是第 k 小的元素。把这些元素全部 "删除"，剩下的作为新的 nums1 数组
     * 如果 pivot = pivot2，那么 nums2[0 .. k/2-1] 都不可能是第 k 小的元素。把这些元素全部 "删除"，剩下的作为新的 nums2 数组
     * 由于我们 "删除" 了一些元素（这些元素都比第 k 小的元素要小），因此需要修改 k 的值，减去删除的数的个数
     */

    int length1 = nums1.length, length2 = nums2.length;
    int index1 = 0, index2 = 0;
    int kthElement = 0;

    while (true) {
        // 边界情况
        if (index1 == length1) {
            return nums2[index2 + k - 1];
        }
        if (index2 == length2) {
            return nums1[index1 + k - 1];
        }
        if (k == 1) {
            return Math.min(nums1[index1], nums2[index2]);
        }
        
        // 正常情况
        int half = k / 2;
        int newIndex1 = Math.min(index1 + half, length1) - 1;
        int newIndex2 = Math.min(index2 + half, length2) - 1;
        int pivot1 = nums1[newIndex1], pivot2 = nums2[newIndex2];
        if (pivot1 <= pivot2) {
            k -= (newIndex1 - index1 + 1);
            index1 = newIndex1 + 1;
        } else {
            k -= (newIndex2 - index2 + 1);
            index2 = newIndex2 + 1;
        }
    }
}

"""





































