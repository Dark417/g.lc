# 128. 最长连续序列







def longestConsecutive(self, nums):
    longest_streak = 0
    num_set = set(nums)

    for num in num_set:
        if num - 1 not in num_set:
            current_num = num
            current_streak = 1

            while current_num + 1 in num_set:
                current_num += 1
                current_streak += 1

            longest_streak = max(longest_streak, current_streak)

    return longest_streak



def longestConsecutive(self, nums):
    if not nums:
        return 0

    nums.sort()

    longest_streak = 1
    current_streak = 1

    for i in range(1, len(nums)):
        if nums[i] != nums[i-1]:
            if nums[i] == nums[i-1]+1:
                current_streak += 1
            else:
                longest_streak = max(longest_streak, current_streak)
                current_streak = 1

    return max(longest_streak, current_streak)



def longestConsecutive(self, nums):
    nums = set(nums)
    best = 0
    for x in nums:
        if x - 1 not in nums:
            y = x + 1
            while y in nums:
                y += 1
            best = max(best, y - x)
    return best


def longestConsecutive(self, nums):
    hash_dict = dict()
    
    max_length = 0
    for num in nums:
        if num not in hash_dict:
            left = hash_dict.get(num - 1, 0)
            right = hash_dict.get(num + 1, 0)
            
            cur_length = 1 + left + right
            if cur_length > max_length:
                max_length = cur_length
            
            hash_dict[num] = cur_length
            hash_dict[num - left] = cur_length
            hash_dict[num + right] = cur_length
            
    return max_length


















