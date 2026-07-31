"""
166.1051. Height Checker
1051. 高度检查器

Students are asked to stand in non-decreasing order of heights for an annual photo.

Return the minimum number of students that must move in order for all students to be standing in non-decreasing order of height.

Notice that when a group of students is selected they can reorder in any possible way 
between themselves and the non selected students remain on their seats.

 

Example 1:

Input: heights = [1,1,4,2,1,3]
Output: 3
Explanation: 
Current array : [1,1,4,2,1,3]
Target array  : [1,1,1,2,3,4]
On index 2 (0-based) we have 4 vs 1 so we have to move this student.
On index 4 (0-based) we have 1 vs 3 so we have to move this student.
On index 5 (0-based) we have 3 vs 4 so we have to move this student.
Example 2:

Input: heights = [5,1,2,3,4]
Output: 5
Example 3:

Input: heights = [1,2,3,4,5]
Output: 0
 

Constraints:

1 <= heights.length <= 100
1 <= heights[i] <= 100

https://leetcode-cn.com/problems/height-checker/solution/onjie-fa-yong-shi-yu-nei-cun-ji-bai-100-javayong-h/

"""



return sum(h1 != h2 for h1, h2 in zip(heights, sorted(heights)))


def heightChecker(self, heights: List[int]) -> int:
        return sum( heights[i]!=sorted(heights)[i]
        for i in range(len(heights))
        )

return sum(map(operator.ne, heights, sorted(heights)))


def heightChecker(self, heights: List[int]) -> int:
    bucket=[0]*101
    for height in heights:
        bucket[height]+=1
    count=0
    j=0
    for i in range(1,101):
        while bucket[i]>=1:
            if heights[j]!=i:
                count+=1
            j+=1
            bucket[i]-=1
    return count




def heightChecker(self, heights: List[int]) -> int:        
    # heights_sorted = sorted(heights)
    # return sum([heights[i]!=heights_sorted[i] for i in range(len(heights))])
    
    cnt = [0]*(100+1) # position i recording the count of the number i 
    for h in heights:
        cnt[h] += 1
    # change count to the accumulative count
    for i in range(1,len(cnt)):
        cnt[i] += cnt[i-1]
    
    heights_sorted = [0]*len(heights)
    res = 0
    for h in heights:
        heights_sorted[cnt[h] - 1] = h
        if heights_sorted[cnt[h] - 1] != heights[cnt[h] - 1]:
            res += 1
        cnt[h] -= 1
    return res


def heightChecker(self, heights: List[int]) -> int:
    max_nr = max(heights)
    # initialize frequency array with 0's
    count = [0] * (max_nr + 1)
    # get frequencies
    for number in heights:
        count[number] += 1
    # create a sumcount array
    sumcount = [0] * (max_nr + 1)
    for index, number in enumerate(count[1:],start=1):
        sumcount[index] = number + sumcount[index-1]
    # sumcount determines the index in sorted array
    # create output array
    output = [0] * len(heights)
    # loop backwards starting with last element for stable sort
    for p in range(len(heights)-1,-1,-1):
        output[sumcount[heights[p]]-1] = heights[p]
        sumcount[heights[p]] -= 1
	# return the difference compared to original array
    result = 0
    for index, number in enumerate(heights):
        if number != output[index]:
            result += 1
    return result












































































































