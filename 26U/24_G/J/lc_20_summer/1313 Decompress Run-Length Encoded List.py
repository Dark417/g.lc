class Solution():
    def decompressRLElist(nums):
        list = []
        for (item, num) in nums:
            list.append([item] * num)
        return list

input = [2,3,4,5]

if __name__ == '__main__':
    sol = Solution.decompressRLElist(input)
    print(sol)
#

# a = [2]
# b = 3
# c = a*b
# print(c)