"""
054.553. Optimal Division
最优除法


Given a list of positive integers, the adjacent integers will perform the float division. For example, [2,3,4] -> 2 / 3 / 4.

However, you can add any number of parenthesis at any position to change the priority of operations. You should find out how to add parenthesis to get the maximum result, and return the corresponding expression in string format. Your expression should NOT contain redundant parenthesis.

Example:
Input: [1000,100,10,2]
Output: "1000/(100/10/2)"
Explanation:
1000/(100/10/2) = 1000/((100/10)/2) = 200
However, the bold parenthesis in "1000/((100/10)/2)" are redundant, 
since they don't influence the operation priority. So you should return "1000/(100/10/2)". 

Other cases:
1000/(100/10)/2 = 50
1000/(100/(10/2)) = 50
1000/100/10/2 = 0.5
1000/100/(10/2) = 2
Note:

The length of the input array is [1, 10].
Elements in the given array will be in range [2, 1000].
There is only one optimal division for each test case.

"""


def optimalDivision(self, nums: List[int]) -> str:
    nums = list(map(str, nums))
    if len(nums) > 2:
        nums[1] = "(" + nums[1]
        nums[-1] = nums[-1] + ")"
    return "/".join(nums)

def optimalDivision(self, nums: List[int]) -> str:
    if len(nums) < 3:
        return '/'.join(str(x) for x in nums)
    return "{}/({})".format(nums[0], "/".join(str(x) for x in nums[1:]))

    return f'{n[0]}/({"/".join(map(str,n[1:]))})' if len(n)>2 else "/".join(map(str,n))

def optimalDivision(self, A):
    A = map(str, A)
    if len(A) <= 2: return '/'.join(A)
    return '{}/({})'.format(A[0], '/'.join(A[1:]))


def optimalDivision(self, nums):
    A = map(str, nums)		#A = list(map(str, nums))
    if len(A) <= 2:
        return '/'.join(A)
    return A[0] + '/(' + '/'.join(A[1:]) + ')'


def optimalDivision(self, nums: List[int]) -> str:
    if len(nums) <= 2: return '/'.join(map(str, nums))
    return f"{nums[0]}/({'/'.join(map(str, nums[1:]))})"


def optimalDivision(self, nums):
    nums = tuple(map(str, nums))
    if len(nums) <= 2:
        return '/'.join(nums)
    return f"{nums[0]}/({'/'.join(nums[1:])})"


def optimalDivision(self, nums):
    stdout = ""
    if len(nums) == 1:
        return "{}".format(nums[0])
    if len(nums) == 2:
        return "{}/{}".format(nums[0], nums[1])

    for i in range(len(nums)):
        if i == len(nums) - 1:
            stdout += "{})".format(nums[i])
            continue
        if i == 0:
            stdout += "{}/(".format(nums[i])
        else:
            stdout += "{}/".format(nums[i])
    return stdout




"""
public class Solution {
    public String optimalDivision(int[] nums) {
        if (nums.length == 1)
            return nums[0] + "";
        if (nums.length == 2)
            return nums[0] + "/" + nums[1];
        StringBuilder res = new StringBuilder(nums[0] + "/(" + nums[1]);
        for (int i = 2; i < nums.length; i++) {
            res.append("/" + nums[i]);
        }
        res.append(")");
        return res.toString();
    }
}
"""





















