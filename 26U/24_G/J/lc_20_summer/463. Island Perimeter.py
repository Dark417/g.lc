"""
463. Island Perimeter
You are given a map in form of a two-dimensional integer grid where 1 represents land and 0 represents water.

Grid cells are connected horizontally/vertically (not diagonally). The grid is completely surrounded by water, and there is exactly one island (i.e., one or more connected land cells).

The island doesn't have "lakes" (water inside that isn't connected to the water around the island). One cell is a square with side length 1. The grid is rectangular, width and height don't exceed 100. Determine the perimeter of the island.


Example:

Input:
[[0,1,0,0],
 [1,1,1,0],
 [0,1,0,0],
 [1,1,0,0]]

Output: 16

Explanation: The perimeter is the 16 yellow stripes in the image below:





"""

input0 = [[0, 1, 0, 0],
          [1, 1, 1, 0],
          [0, 1, 0, 0],
          [1, 1, 0, 0]]




return sum(sum(map(operator.ne, [0] + row, row + [0]))
               for row in grid + map(list, zip(*grid)))


def islandPerimeter(self, grid: List[List[int]]) -> int:
    r, c = len(grid), len(grid[0])
    sm = sum(i for r in grid for i in r)
    sm *= 4
    for i in range(r):
        for j in range(c):
            if j != c-1 and grid[i][j] == grid[i][j+1] == 1:
                sm -= 2
            if i != r-1 and grid[i][j] == grid[i+1][j] == 1:
                sm -= 2
    return sm


def islandPerimeter(self, grid):
    m, n, Perimeter = len(grid), len(grid[0]), 0

    for i in range(m):
        for j in range(n):
            Perimeter += 4*grid[i][j]
            if i > 0:   Perimeter -= grid[i][j]*grid[i-1][j]
            if i < m-1: Perimeter -= grid[i][j]*grid[i+1][j]
            if j > 0:   Perimeter -= grid[i][j]*grid[i][j-1]
            if j < n-1: Perimeter -= grid[i][j]*grid[i][j+1]
                
    return Perimeter



"""
iterate
class Solution {
    static int[] dx = {0, 1, 0, -1};
    static int[] dy = {1, 0, -1, 0};

    public int islandPerimeter(int[][] grid) {
        int n = grid.length, m = grid[0].length;
        int ans = 0;
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < m; ++j) {
                if (grid[i][j] == 1) {
                    int cnt = 0;
                    for (int k = 0; k < 4; ++k) {
                        int tx = i + dx[k];
                        int ty = j + dy[k];
                        if (tx < 0 || tx >= n || ty < 0 || ty >= m || grid[tx][ty] == 0) {
                            cnt += 1;
                        }
                    }
                    ans += cnt;
                }
            }
        }
        return ans;
    }
}





dfs
class Solution {
    static int[] dx = {0, 1, 0, -1};
    static int[] dy = {1, 0, -1, 0};

    public int islandPerimeter(int[][] grid) {
        int n = grid.length, m = grid[0].length;
        int ans = 0;
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < m; ++j) {
                if (grid[i][j] == 1) {
                    ans += dfs(i, j, grid, n, m);
                    System.out.println(ans);
                }
            }
        }
        return ans;
    }

    public int dfs(int x, int y, int[][] grid, int n, int m) {
        if (x < 0 || x >= n || y < 0 || y >= m || grid[x][y] == 0) {
            return 1;
        }
        if (grid[x][y] == 2) {
            return 0;
        }
        grid[x][y] = 2;
        int res = 0;
        for (int i = 0; i < 4; ++i) {
            int tx = x + dx[i];
            int ty = y + dy[i];
            res += dfs(tx, ty, grid, n, m);
        }
        return res;
    }
}


public int islandPerimeter(int[][] grid) {
    for (int r = 0; r < grid.length; r++) {
        for (int c = 0; c < grid[0].length; c++) {
            if (grid[r][c] == 1) {
                // 题目限制只有一个岛屿，计算一个即可
                return dfs(grid, r, c);
            }
        }
    }
    return 0;
}

int dfs(int[][] grid, int r, int c) {
    if (!(0 <= r && r < grid.length && 0 <= c && c < grid[0].length)) {
        return 1;
    }
    if (grid[r][c] == 0) {
        return 1;
    }
    if (grid[r][c] != 1) {
        return 0;
    }
    grid[r][c] = 2;
    return dfs(grid, r - 1, c)
        + dfs(grid, r + 1, c)
        + dfs(grid, r, c - 1)
        + dfs(grid, r, c + 1);
}




"""





def isConnected(a, b):
    if a[0] == b[0] or a[1] == b[1]:
        print(a, b)
        return True
    return False


def islandPerimeter(grid):
    island = []
    res = 0
    connected = 0
    for i in range(len(input0)):
        for j in range(len(input0[i])):
            if input0[i][j] == 1:
                # island += [i, j]
                island.append([i, j])

    ttl = len(island) * 4
    # island = [[i, j] for j in input0[i] for i in input0 if j*i == 1]

    print(island)

    a = 0
    b = 1
    for i in range(a, len(island)-1):
        for j in range(b, len(island)):
            if isConnected(island[i], island[j]):
                connected += 1
            b += 1
        a += 1

    res = ttl - connected * 2

    return res


res = islandPerimeter(input0)







