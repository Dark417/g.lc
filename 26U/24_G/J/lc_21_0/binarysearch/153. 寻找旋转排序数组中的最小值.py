# 153. 寻找旋转排序数组中的最小值
# https://leetcode-cn.com/problems/find-minimum-in-rotated-sorted-array/solution/er-fen-cha-zhao-wei-shi-yao-zuo-you-bu-dui-cheng-z/

def findMin(self, nums: List[int]) -> int:    
    low, high = 0, len(nums) - 1
    while low < high:
        pivot = low + (high - low) // 2
        if nums[pivot] < nums[high]:
            high = pivot 
        else:
            low = pivot + 1
    return nums[low]




class Solution:
    def findMin(self, nums: List[int]) -> int:
        left, right = 0, len(nums) - 1          # 左闭右闭区间，如果用右开区间则不方便判断右值
        while left < right:                     # 循环不变式，如果left == right，则循环结束
            mid = (left + right) >> 1           # 地板除，mid更靠近left
            if nums[mid] > nums[right]:         # 中值 > 右值，最小值在右半边，收缩左边界
                left = mid + 1                  # 因为中值 > 右值，中值肯定不是最小值，左边界可以跨过mid
            elif nums[mid] < nums[right]:       # 明确中值 < 右值，最小值在左半边，收缩右边界
                right = mid                     # 因为中值 < 右值，中值也可能是最小值，右边界只能取到mid处
        return nums[left]                       # 循环结束，left == right，最小值输出nums[left]或nums[right]均可



# max + 1
class Solution:
    def findMin(self, nums: List[int]) -> int:
        left, right = 0, len(nums) - 1   
        while left < right:          
            mid = (left + right + 1) >> 1           # 先加一再除，mid更靠近右边的right     
            if nums[left] < nums[mid]:         
                left = mid                          # 向右移动左边界
            elif nums[left] > nums[mid]:       
                right = mid - 1                     # 向左移动右边界
        return nums[(right + 1) % len(nums)]        # 最大值向右移动一位就是最小值了（需要考虑最大值在最右边的情况，右移一位后对数组长度取余）




class Solution:
    def findMin(self, nums: List[int]) -> int:
        left, right = 0, len(nums) - 1    
        while left <= right:                    # 循环的条件选为左闭右闭区间left <= right
            mid = (left + right) >> 1
            if nums[mid] >= nums[right]:        # 注意是当中值大于等于右值时，      
                left = mid + 1                  # 将左边界移动到中值的右边
            else:                               # 当中值小于右值时
                right = mid                     # 将右边界移动到中值处
        return nums[right]                      # 最小值返回nums[right]





def findMin(self, nums):
    if len(nums) == 1:
        return nums[0]

    left = 0
    right = len(nums) - 1

    if nums[right] > nums[0]:
        return nums[0]

    while right >= left:
        mid = left + (right - left) / 2
        if nums[mid] > nums[mid + 1]:
            return nums[mid + 1]
        if nums[mid - 1] > nums[mid]:
            return nums[mid]

        if nums[mid] > nums[0]:
            left = mid + 1
        else:
            right = mid - 1

