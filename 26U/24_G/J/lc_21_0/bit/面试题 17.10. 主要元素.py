# 面试题 17.10. 主要元素

def majorityElement(self, nums: List[int]) -> int:
    if not nums:
        return -1
    major, vote = None, 0
    for num in nums:
        if vote == 0:
            major = num
            vote += 1
        else:
            if num == major:
                vote += 1
            else:
                vote -= 1
    if vote == 0:
        return -1
    
    identify = 0
    for num in nums:
        if num == major:
            identify += 1
            if identify > len(nums)/2:
                return major
    return -1

