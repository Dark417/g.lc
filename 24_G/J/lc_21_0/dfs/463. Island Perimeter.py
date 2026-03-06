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
print(res)
