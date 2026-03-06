# 54. 螺旋矩阵



def spiralOrder(self, matrix:[[int]]) -> [int]:
    if not matrix: return []
    l, r, t, b, res = 0, len(matrix[0]) - 1, 0, len(matrix) - 1, []
    while True:
        for i in range(l, r + 1): res.append(matrix[t][i]) # left to right
        t += 1
        if t > b: break
        for i in range(t, b + 1): res.append(matrix[i][r]) # top to bottom
        r -= 1
        if l > r: break
        for i in range(r, l - 1, -1): res.append(matrix[b][i]) # right to left
        b -= 1
        if t > b: break
        for i in range(b, t - 1, -1): res.append(matrix[i][l]) # bottom to top
        l += 1
        if l > r: break
    return res





def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
    if not matrix or not matrix[0]:
        return list()
    
    rows, columns = len(matrix), len(matrix[0])
    visited = [[False] * columns for _ in range(rows)]
    total = rows * columns
    order = [0] * total

    directions = [[0, 1], [1, 0], [0, -1], [-1, 0]]
    row, column = 0, 0
    directionIndex = 0
    for i in range(total):
        order[i] = matrix[row][column]
        visited[row][column] = True
        nextRow, nextColumn = row + directions[directionIndex][0], column + directions[directionIndex][1]
        if not (0 <= nextRow < rows and 0 <= nextColumn < columns and not visited[nextRow][nextColumn]):
            directionIndex = (directionIndex + 1) % 4
        row += directions[directionIndex][0]
        column += directions[directionIndex][1]
    return order


def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
    if not matrix or not matrix[0]:
        return list()
    
    rows, columns = len(matrix), len(matrix[0])
    order = list()
    left, right, top, bottom = 0, columns - 1, 0, rows - 1
    while left <= right and top <= bottom:
        for column in range(left, right + 1):
            order.append(matrix[top][column])
        for row in range(top + 1, bottom + 1):
            order.append(matrix[row][right])
        if left < right and top < bottom:
            for column in range(right - 1, left, -1):
                order.append(matrix[bottom][column])
            for row in range(bottom, top, -1):
                order.append(matrix[row][left])
        left, right, top, bottom = left + 1, right - 1, top + 1, bottom - 1
    return order



def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
    res = []
    while matrix:
        res += matrix.pop(0)
        matrix = list(zip(*matrix))[::-1]
    return res




