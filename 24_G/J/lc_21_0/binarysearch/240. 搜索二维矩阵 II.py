# 240. 搜索二维矩阵 II

# 本题没有确保「每行的第一个整数大于前一行的最后一个整数」，因此我们无法采取「两次二分」的做法



def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
    for row in matrix:
        for element in row:
            if element == target:
                return True
    return False


def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
    for row in matrix:
        idx = bisect.bisect_left(row, target)
        if idx < len(row) and row[idx] == target:
            return True
    return False


def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
    m, n = len(matrix), len(matrix[0])
    x, y = 0, n - 1
    while x < m and y >= 0:
        if matrix[x][y] == target:
            return True
        if matrix[x][y] > target:
            y -= 1
        else:
            x += 1
    return False

def findNumberIn2DArray(self, matrix: List[List[int]], target: int) -> bool:
    i, j = len(matrix) - 1, 0
    while i >= 0 and j < len(matrix[0]):
        if matrix[i][j] > target: i -= 1
        elif matrix[i][j] < target: j += 1
        else: return True
    return False



def findNumberIn2DArray(self, matrix: List[List[int]], target: int) -> bool:
    for row in matrix:
        l, r = 0, len(row)
        while l < r:
            mid = l + (r - l) // 2
            if row[mid] == target:
                return True
            elif target < row[mid]:
                r = mid
            else:
                l = mid + 1
    return False

        

"""
public boolean searchMatrix(int[][] matrix, int target) {
    int m = matrix.length, n = matrix[0].length;
    for (int i = 0; i < m; i++) {
        int l = 0, r = n - 1;
        while (l < r) {
            int mid = l + r + 1 >> 1;
            if (matrix[i][mid] <= target) l = mid;
            else r = mid - 1;
        }
        if (matrix[i][r] == target) return true;
    }
    return false;
}


public boolean searchMatrix(int[][] matrix, int target) {
    int m = matrix.length, n = matrix[0].length;
    for (int i = 0; i < n; i++) {
        int l = 0, r = m - 1;
        while (l < r) {
            int mid = l + r + 1 >> 1;
            if (matrix[mid][i] <= target) l = mid;
            else r = mid - 1;
        }
        if (matrix[r][i] == target) return true;
    }
    return false;
}


public boolean searchMatrix(int[][] matrix, int target) {
    int m = matrix.length, n = matrix[0].length;
    int r = 0, c = n - 1;
    while (r < m && c >= 0) {
        if (matrix[r][c] < target) r++;
        else if (matrix[r][c] > target) c--;
        else return true;
    }
    return false;
}




"""


