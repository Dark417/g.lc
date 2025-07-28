# 27. 移除元素


"""
public int removeElement(int[] nums, int val) {
    int ans = 0;
    for(int num: nums) {
        if(num != val) {
            nums[ans] = num;
            ans++;
        }
    }
    return ans;
}


public int removeElement(int[] nums, int val) {
    int i = 0;
    for (int j = 0; j < nums.length; j++) {
        if (nums[j] != val) {
            nums[i] = nums[j];
            i++;
        }
    }
    return i;
}

public int removeElement(int[] nums, int val) {
    int i = 0;
    int n = nums.length;
    while (i < n) {
        if (nums[i] == val) {
            nums[i] = nums[n - 1];
            n--;
        } else {
            i++;
        }
    }
    return n;
}

"""


def removeElement(self, nums: List[int], val: int) -> int:
	n = len(nums)
	i = 0
	while i < n:
		if nums[i] == val:
			nums[i] = nums[n - 1]
			n -= 1
		else:
			i += 1
	return n


def removeElement(self, nums: List[int], val: int) -> int:
    i, j = 0, len(nums) - 1
    while i <= j:
        if nums[i] == val:
            if nums[j] != val:
                nums[i] = nums[j]
                j -= 1
            else:
                while j > i and nums[j] == val:
                    j -= 1
                nums[i] = nums[j]
                j -= 1
                if j < i:
                    break
        i += 1
    return i














