def twoSum(self, nums: List[int], target: int) -> List[int]:
    if len(nums) <= 1:
        return False
    buff_dict = {}
    for i in range(len(nums)):
        if nums[i] in buff_dict:
            return [buff_dict[nums[i]], i]
        else:
            buff_dict[target - nums[i]] = i




def main():
    input = [2, 4, 7, 9, 11]

    twoSum(input, 11)

if __name__ == '__main__':
    main()