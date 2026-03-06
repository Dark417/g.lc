# 74. 搜索二维矩阵
def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
    for m in range(len(matrix)):
        if matrix[m][0] <= target and matrix[m][-1] >= target:
            l, r = 0, len(matrix[0]) - 1
            while l <= r:
                mid = l + (r - l) // 2
                if matrix[m][mid] == target:
                    return True
                elif matrix[m][mid] < target:
                    l = mid + 1
                else:
                    r = mid - 1
    return False




"""
public boolean searchMatrix(int[][] matrix, int target) {
    int rowIndex = binarySearchFirstColumn(matrix, target);
    if (rowIndex < 0) {
        return false;
    }
    return binarySearchRow(matrix[rowIndex], target);
}

public int binarySearchFirstColumn(int[][] matrix, int target) {
    int low = -1, high = matrix.length - 1;
    while (low < high) {
        int mid = (high - low + 1) / 2 + low;
        if (matrix[mid][0] <= target) {
            low = mid;
        } else {
            high = mid - 1;
        }
    }
    return low;
}

public boolean binarySearchRow(int[] row, int target) {
    int low = 0, high = row.length - 1;
    while (low <= high) {
        int mid = (high - low) / 2 + low;
        if (row[mid] == target) {
            return true;
        } else if (row[mid] > target) {
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }
    return false;
}




public boolean searchMatrix(int[][] matrix, int target) {
    int m = matrix.length, n = matrix[0].length;
    int low = 0, high = m * n - 1;
    while (low <= high) {
        int mid = (high - low) / 2 + low;
        int x = matrix[mid / n][mid % n];
        if (x < target) {
            low = mid + 1;
        } else if (x > target) {
            high = mid - 1;
        } else {
            return true;
        }
    }
    return false;
}


"""























