"""
961. N-Repeated Element in Size 2N Array

In a array A of size 2N, there are N+1 unique elements, and exactly one of these elements is repeated N times.

Return the element repeated N times.

Example 1:
Input: [1,2,3,3]
Output: 3
Example 2:

Input: [2,1,2,5,3,2]
Output: 2
Example 3:

Input: [5,1,5,2,5,3,5,4]
Output: 5
 

Note:
4 <= A.length <= 10000
0 <= A[i] < 10000
A.length is even



"""
input0 = [2,1,2,5,3,2]



# x=random.choice(A)

# if adjacent equal
for(i=0;i<ASize-1;i++)
    if(A[i]==A[i+1])
        return A[i];

return A[0];

#
def repeatedNTimes(self, A: List[int]) -> int:
	B = set(A)
	return (sum(A) - sum(B)) // (len(A) - len(B))


def repeatedNTimes(self, A):
    return int((sum(A)-sum(set(A))) // (len(A)//2-1))
    return int((sum(A)-sum(set(A))) // 
                   (len(A) -len(set(A))))

def repeatedNTimes(self, A: List[int]) -> int:
    d = {}
    for num in A:
        if num in d: #d.keys()
            return num
        else:
            d[num] = 1

    unique = set() # empty set
    for i in A:
        if i in unique:     # if 'i' element already exists then it is a duplicate
            return i          # loop is exited as value is directly returned
        unique.add(i)

	R=[]
    for i in A:
        if i in R:
            return i
        else:
            R.append(i)

    lst = []
    for i in range(len(A)):
        if A[i] not in lst:
            lst.append(A[i])
        else:
            return(A[i])

# D
def repeatN(n):
	dic = {}
	res = 0

	target = len(n)//2

	for i in n:
		if str(i) in dic:
			dic[str(i)] += 1
		else:
			dic[str(i)] = 1

		if dic[str(i)] == target:
			return str(i)

output = repeatN(input0)
print(output)










