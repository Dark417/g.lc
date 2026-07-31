# 1150. 检查一个数是否在数组中占绝大多数

helper(t) - helper(t - 1)

def isMajorityElement(self, nums: List[int], target: int) -> bool:
    left,right = 0, len(nums)-1
    while(left<=right):
        mid = (left+right)//2
        if nums[mid]<target:
            left = mid+1
        else:
            right = mid-1
    if left+len(nums)//2>len(nums)-1:
        return False
    if nums[left+len(nums)//2]==target:
        return True
    else:
        return False























