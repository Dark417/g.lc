# 704. 二分查找

def search(self, nums: List[int], target: int) -> int:
    def bs(i:int, j:int):
        if i>j: return -1
        m = (i+j)//2
        if target == nums[m]: return m
        elif target > nums[m]: return bs(m+1, j)
        else: return bs(i, m-1)
        
    return bs(0, len(nums)-1)







