"""
144.1470. Shuffle the Array
重新排列数组

Given the array nums consisting of 2n elements in the form [x1,x2,...,xn,y1,y2,...,yn].

Return the array in the form [x1,y1,x2,y2,...,xn,yn].

 

Example 1:

Input: nums = [2,5,1,3,4,7], n = 3
Output: [2,3,5,4,1,7] 
Explanation: Since x1=2, x2=5, x3=1, y1=3, y2=4, y3=7 then the answer is [2,3,5,4,1,7].
Example 2:

Input: nums = [1,2,3,4,4,3,2,1], n = 4
Output: [1,4,2,3,3,2,4,1]
Example 3:

Input: nums = [1,1,2,2], n = 2
Output: [1,2,1,2]
 

Constraints:

1 <= n <= 500
nums.length == 2n
1 <= nums[i] <= 10^3


"""





return [nums[i // 2 + i % 2 * n] for i in range(2 * n)]
return list(sum(zip(nums[:n],nums[n:]), ()))

return reduce(lambda x, y : x+y, zip(nums[:n], nums[n:]))

return sum(([nums[i], nums[i+n]] for i in range(n)), [])
return sum([nums[i::n] for i in range(n)],[])


# *
def shuffle(self, nums: List[int], n: int) -> List[int]:
    getDesireIdx = lambda i: i*2 if i<n else (i-n)*2+1
    for i in range(2*n):
        j=i
        while nums[i]>=0:
            j=getDesireIdx(j)
            nums[i],nums[j]=nums[j],-nums[i]
    for i in range(2*n):
        nums[i]=-nums[i]
    return nums


def shuffle(self, nums: List[int], n: int) -> List[int]:
    for i in range(n):
        m = n - i
    
        for k in range(i):
            nums[m], nums[m+1] = nums[m+1], nums[m]
            m += 2
    
    return nums





def shuffle(self, nums: List[int], n: int) -> List[int]:
    def gen(A):
        for i in range(n): 
            yield from (A[i], A[i+n])
    return list(gen(nums))



def shuffle(self,nums,n):
	nums[::2],nums[1::2]=nums[:n],nums[n:]
	return nums


def shuffle(self, nums: List[int], n: int) -> List[int]:
        res = []
        for i, j in zip(nums[:n],nums[n:]):
            res += [i,j]
        return res


def shuffle(self, nums: List[int], n: int) -> List[int]:
	res = [1] * n
	for i in range(n):
		res[i] = nums[i] if i%2==1 else nums[i+len(nums)//2]
	return res


def shuffle(self, nums: List[int], n: int) -> List[int]:
    res = [1]*2*n
    for i in range(2*n):
        # res[i] = i % 2 == 0 ? nums[i/2] : nums[n + i/2];
        res[i] = nums[i//2] if i%2==0 else nums[n+i//2]        
    return res


def shuffle(self, nums: List[int], n: int) -> List[int]:
    res = [1] * 2*n
    for i in range(len(res)):
        if (i+1)%2==1:
            res[i] = nums[(i+1)//2]
        else:
            res[i] = nums[(i+1)//2-1 + n]
    return res


def shuffle(self, nums: List[int], n: int) -> List[int]:
    res = [1] *2*n
    for i in range(n):
        res[i*2] = nums[i]
        res[i*2+1] = nums[i+n]
    return res







def shuffle(self, nums: List[int], n: int) -> List[int]:
    x = nums[:len(nums)//2]		# n
    y = nums[len(nums)//2:]
    res = []
    for i in range(len(nums)//2):
        res += [x[i], y[i]]
    return res


def shuffle(self, nums: List[int], n: int) -> List[int]:
    for i in range(len(nums)//2):
        x = nums.pop(i + len(nums)//2)
        nums.insert(i*2+1, x)
    return nums





























