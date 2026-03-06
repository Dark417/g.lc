"""
162.1252. Cells with Odd Values in a Matrix
奇数值单元格的数目

Given n and m which are the dimensions of a matrix initialized by zeros and given an 
array indices where indices[i] = [ri, ci]. For each pair of [ri, ci] you have to increment all cells in row ri and column ci by 1.

Return the number of cells with odd values in the matrix after applying the increment to all indices.

 

Example 1:


Input: n = 2, m = 3, indices = [[0,1],[1,1]]
Output: 6
Explanation: Initial matrix = [[0,0,0],[0,0,0]].
After applying first increment it becomes [[1,2,1],[0,1,0]].
The final matrix will be [[1,3,1],[1,3,1]] which contains 6 odd numbers.
Example 2:


Input: n = 2, m = 2, indices = [[1,1],[0,0]]
Output: 0
Explanation: Final matrix = [[2,2],[2,2]]. There is no odd number in the final matrix.
 

Constraints:

1 <= n <= 50
1 <= m <= 50
1 <= indices.length <= 100
0 <= indices[i][0] < n
0 <= indices[i][1] < m

"""

def oddCells(self, n: int, m: int, indices: List[List[int]]) -> int:
    mat = [[0]  * m for _ in range(n)]
    for i in indices:
        for k in range(m):
            mat[i[0]][k] += 1
        for k in range(n):
            mat[k][i[1]] += 1
    return sum(i%2 for j in mat for i in j)



def oddCells(self, n: int, m: int, indices: List[List[int]]) -> int:
	odd_count = 0
	rows = [0] * n
	cols = [0] * m

	for i, j in indices:
		rows[i] = rows[i] ^ 1
		cols[j] = cols[j] ^ 1

	for i in range(n):
		for j in range(m):
			if(rows[i] ^ cols[j] == 1): odd_count += 1

	return odd_count



def oddCells(self, n: int, m: int, indices: List[List[int]]) -> int:
        yy=set()
        xx=set()
        for y,x in indices:
            if y in yy:yy.remove(y)
            else:yy.add(y)
            if x in xx:xx.remove(x)
            else:xx.add(x)
        a=len(yy)
        b=len(xx)
        return a*(m-b)+b*(n-a)

def oddCells(self, n: int, m: int, indices: List[List[int]]) -> int:
        rows, cols, res = [0] * n, [0] * m, 0  # initialization
        for i, j in indices:
            rows[i], cols[j] = rows[i] ^ 1, cols[j] ^ 1  # 0 -> even, 1 -> odd
        for i in range(n):
            for j in range(m):
                res += 1 if rows[i] ^ cols[j] == 1 else 0
        return res


def oddCells(self, n: int, m: int, indices: List[List[int]]) -> int:
        
        x,y = [0]*n,[0]*m
        for r,c in indices:
            x[r] += 1
            y[c] += 1

        return sum([ (r+c)%2 for c in y for r in x]) 

def oddCells(self, n: int, m: int, indices: List[List[int]]) -> int:
        row_counter = {i:False for i in range(n)}
        column_counter = {i:False for i in range(m)}
        for r, c in indices:
            row_counter[r] = not row_counter[r]
            column_counter[c] = not column_counter[c]
        sum_row = sum(row_counter.values())
        sum_col = sum(column_counter.values())
        return (sum_row * m) + (sum_col * (n - sum_row)) - (sum_row * sum_col)



# https://leetcode-cn.com/problems/cells-with-odd-values-in-a-matrix/solution/python3xiao-bai-jie-fa-you-qian-ru-shen-jian-dan-y/
def oddCells(self, n: int, m: int, indices: List[List[int]]) -> int:
    res = 0
    # 用 0 构造矩阵
    arr = [[0] * m for _ in range(n)]
    # 模拟矩阵 +1 操作
    for row, col in indices:
        for j in range(m):
            arr[row][j] += 1
        for i in range(n):
            arr[i][col] += 1
    # 遍历矩阵，数奇数的个数
    for row in arr:
        for i in row:
            if i % 2 == 1:
                res += 1
    return res




def oddCells(self, n: int, m: int, indices: List[List[int]]) -> int:
    res = 0
    # 用 False 构造矩阵，因为默认0是偶数
    arr = [[False] * m for _ in range(n)]
    # 模拟矩阵 +1 操作，+1 意味着取反
    for row, col in indices:
        for j in range(m):
            arr[row][j] = not arr[row][j]
        for i in range(n):
            arr[i][col] = not arr[i][col]
    # 遍历矩阵，数True的个数
    for row in arr:
        for i in row:
            if i:
                res += 1
    return res


def oddCells(self, n: int, m: int, indices: List[List[int]]) -> int:
    rows = [False] * n
    cols = [False] * m
    res = 0
    # 老规矩，取反，不 + 1
    for r, c in indices:
        rows[r] = not rows[r]
        cols[c] = not cols[c]
    # 遍历rows 和 cols，（r, c）作为坐标
    for r in range(n):
        for c in range(m):
            # 奇数 + 偶数 = 奇数， 偶数 + 偶数 = 偶数， 奇数 + 奇数 = 偶数
            # 即为：False + False = True, True + True = True, False + True = False
            # 两者 异或 即可
            if rows[r] ^ cols[c]:
                res += 1
    return res



def oddCells(self, n: int, m: int, indices: List[List[int]]) -> int:
    rows = [False] * n
    cols = [False] * m
    res = 0

    for r, c in indices:
        rows[r] = not rows[r]
        cols[c] = not cols[c]
    
    # rows数组里，True和False的个数
    rows_true = rows.count(True)
    rows_false = n - rows_true

    cols_true = cols.count(True)
    cols_false = m - cols_true

    res = rows_true * cols_false + rows_false * cols_true
    return res




































































































