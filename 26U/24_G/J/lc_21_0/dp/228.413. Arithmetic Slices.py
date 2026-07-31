"""
228.413. Arithmetic Slices
等差数列划分

A sequence of numbers is called arithmetic if it consists of at least three elements and if the difference between any two consecutive elements is the same.

For example, these are arithmetic sequences:

1, 3, 5, 7, 9
7, 7, 7, 7
3, -1, -5, -9
The following sequence is not arithmetic.

1, 1, 2, 5, 7
 
A zero-indexed array A consisting of N numbers is given. A slice of that array is any pair of integers (P, Q) such that 0 <= P < Q < N.

A slice (P, Q) of the array A is called arithmetic if the sequence:
A[P], A[P + 1], ..., A[Q - 1], A[Q] is arithmetic. In particular, this means that P + 1 < Q.

The function should return the number of arithmetic slices in the array A.

 
Example:

A = [1, 2, 3, 4]

return: 3, for 3 arithmetic slices in A: [1, 2, 3], [2, 3, 4] and [1, 2, 3, 4] itself.
"""



def numberOfArithmeticSlices(self, A: List[int]) -> int:
    res = diff = 0
    count = 1
    A += [float("inf")]
    for i in range(len(A)-1):
        if A[i+1] - A[i] != diff:
            diff = A[i+1] - A[i]
            if count >= 3:
                res += (count-1)*(count-2)//2
                continue
            count = 1
        else:
            count += 1
    return res


def numberOfArithmeticSlices(self, A: List[int]) -> int:
	res = c = 0
	for i in range(2, len(A)):
		if A[i] - A[i-1] == A[i-1] - A[i-2]:
			c += 1
		else:
			res += (c+1)*(c+2)/2
			c = 0
	return res




def numberOfArithmeticSlices(self, A: List[int]) -> int:
    dp = [0] * len(A)
    count = 0
    for i in range(2, len(A)):
        if A[i] - A[i-1] == A[i-1] - A[i-2]:
            dp[i] = dp[i-1] + 1
            count += dp[i]
    return count



def numberOfArithmeticSlices(self, A: List[int]) -> int:
	dp = cnt = 0
	for i in range(2, len(A)):
		if A[i] - A[i-1] == A[i-1] - A[i-2]:
			dp = 1 + dp
			cnt += dp
		else:
			dp = 0
	return cnt





"""
public int numberOfArithmeticSlices(int[] A) {
        int count = 0;
        for (int s = 0; s < A.length - 2; s++) {
            int d = A[s + 1] - A[s];
            for (int e = s + 2; e < A.length; e++) {
                int i = 0;
                for (i = s + 1; i <= e; i++)
                    if (A[i] - A[i - 1] != d)
                        break;
                if (i > e)
                    count++;
            }
        }
        return count;
    }


"""

"""
public int numberOfArithmeticSlices(int[] A) {
        int count = 0;
        for (int s = 0; s < A.length - 2; s++) {
            int d = A[s + 1] - A[s];
            for (int e = s + 2; e < A.length; e++) {
                if (A[e] - A[e - 1] == d)
                    count++;
                else
                    break;
            }
        }
        return count;
    }

"""


"""
int sum = 0;
public int numberOfArithmeticSlices(int[] A) {
    slices(A, A.length - 1);
    return sum;
}
public int slices(int[] A, int i) {
    if (i < 2)
        return 0;
    int ap = 0;
    if (A[i] - A[i - 1] == A[i - 1] - A[i - 2]) {
        ap = 1 + slices(A, i - 1);
        sum += ap;
    } else
        slices(A, i - 1);
    return ap;
}
"""





























































