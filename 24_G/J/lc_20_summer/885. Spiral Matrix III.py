"""
On a 2 dimensional grid with R rows and C columns, we start at (r0, c0) facing east.
Here, the north-west corner of the grid is at the first row and column, and the south-east corner of the grid is at the last row and column.
Now, we walk in a clockwise spiral shape to visit every position in this grid.
Whenever we would move outside the boundary of the grid, we continue our walk outside the grid (but may return to the grid boundary later.)

Eventually, we reach all R * C spaces of the grid.

Return a list of coordinates representing the positions of the grid in the order they were visited.

Example 1:

Input: R = 1, C = 4, r0 = 0, c0 = 0
Output: [[0,0],[0,1],[0,2],[0,3]]

Example 2:

Input: R = 5, C = 6, r0 = 1, c0 = 4
Output: [[1,4],[1,5],[2,5],[2,4],[2,3],[1,3],[0,3],[0,4],[0,5],[3,5],[3,4],[3,3],[3,2],[2,2],[1,2],[0,2],[4,5],[4,4],[4,3],[4,2],[4,1],[3,1],[2,1],[1,1],[0,1],[4,0],[3,0],[2,0],[1,0],[0,0]]

"""
#input1: R = 1, C = 4, r0 = 0, c0 = 0
#input2: R = 5, C = 6, r0 = 1, c0 = 4

"""
while steps < all_grid
    when get out of the boundary, jump to the return point
    walk e, s, w, n


"""

def rtmd(R, C, r0, c0):

    all_grids = R * C   #total points of travel
    cur = [r0, c0]      #current position
    steps = [cur]       #travel history, list of positions
    n_steps = 0         #number of steps
    face = 1            #1 east, 2 south, 3 west, 4 north

    while n_steps < all_grids:
        if face == 1:
            if c0 < C:
                c0 += 1
                n_steps += 1
                steps.append[r0, c0]
            else:
                if r0 < R:
                    down
                else:
                    left



            if n_steps = all_grids:
                break
            else if c0 = C
                face = 2

        if




    return steps