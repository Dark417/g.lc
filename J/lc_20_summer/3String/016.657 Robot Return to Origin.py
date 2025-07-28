"""
016.657	Robot Return to Origin


There is a robot starting at position (0, 0), the origin, on a 2D plane. 
Given a sequence of its moves, judge if this robot ends up at (0, 0) after it completes its moves.

The move sequence is represented by a string, and the character moves[i] 
represents its ith move. Valid moves are R (right), L (left), U (up), and D (down). 
If the robot returns to the origin after it finishes all of its moves, return true. Otherwise, return false.

Note: The way that the robot is "facing" is irrelevant. 
"R" will always make the robot move to the right once, "L" will always make it move left, etc. 
Also, assume that the magnitude of the robot's movement is the same for each move.

Example 1:

Input: "UD"
Output: true 
Explanation: The robot moves up once, and then down once. 
All moves have the same magnitude, so it ended up at the origin where it started. Therefore, we return true.
 

Example 2:

Input: "LL"
Output: false
Explanation: The robot moves left twice. 
It ends up two "moves" to the left of the origin. We return false because it is not at the origin at the end of its moves.




"""

def judgeCircle(self, moves):
    return not sum(1j**'RUL'.find(m) for m in moves)

"""
https://leetcode.com/problems/robot-return-to-origin/discuss/106368/Very-short-Python-and-Ruby
 'RUL' is just a string, as the problem statement mentions "Valid moves are R (right), L (left), U (up), and D (down).".
'RUL'.find(m) returns the first index of m in 'RUL' if m exists in it, otherwise, it returns -1, so it returns 0 for 'R' (if m == 'R'), 1 for 'U', 2 for 'L', -1 for 'D'.
1j is the imaginary unit, 1j**'RUL'.find(m) does exponential calculation of 1j and the return value of 'RUL'.find(m), 1j ** 0 == 1, 1j ** 1 == 1j , 1j ** 2 == -1, 1j ** -1 == -1j
"""


def judgeCircle(self, moves):

    return moves.count("U") == moves.count("D") and moves.count("L") == moves.count("R")


from collections import Counter

class Solution:
    def judgeCircle(self, moves: str) -> bool:
        count = Counter(moves)
        return count['L'] == count['R'] and count['U'] == count['D']



def judgeCircle(self, moves):
    d = {'U': 1, 'D': -1, 'L': 1j, 'R': -1j}
    return sum(d[c] for c in moves) == 0


def judgeCircle(self, moves: str) -> bool:
        dic={'R':0,'L':0,'U':0,'D':0}
        for i in moves:
            dic[i]+=1
        if dic['R']!=dic['L'] or dic['U']!=dic['D']:
            return False
        return True


def judgeCircle(self, moves):
    x = y = 0
    for move in moves:
        if move == 'U': y -= 1
        elif move == 'D': y += 1
        elif move == 'L': x -= 1
        elif move == 'R': x += 1

    return x == y == 0
    return (x==0) and (y==0)


def judgeCircle(self, moves: str) -> bool:
    u = d = l = r = 0
    for move in moves:
        if move == 'U':
            u += 1
        elif move == "D":
            d += 1
        elif move == 'L':
            l += 1
        elif move == 'R':
            r += 1
    return u == d and l == r


def judgeCircle(self, moves: str) -> bool:
        m = ['L', 'R', 'U', 'D']

        count_x_move, count_y_move = 0, 0
        for char in moves:
            if char not in m:
                return False

            if char == 'L':
                count_x_move -= 1
            if char == 'R':
                count_x_move += 1
            if char == 'D':
                count_y_move -= 1
            if char == 'U':
                count_y_move += 1

        if count_x_move == 0 and count_y_move == 0:
            return True
        return False


def judgeCircle(self, moves: str) -> bool:
    d = {'R':[1,0],
        'L':[-1,0],
        'U':[0,1],
        'D':[0,-1]}
    p = [0,0]
    for w in moves:
        m = d[w]
        p[0]+=m[0]
        p[1]+=m[1]
    return p == [0,0]

#
    move_r = [0,0]
        for i in range(len(moves)):
            if moves[i] == "U":
                move_r[0] += 1
            elif moves[i] == "D":
                move_r[0] -= 1
            if moves[i] == "L":
                move_r[1] += 1
            elif moves[i] == "R":
                move_r[1] -= 1
        if move_r == [0,0]:
            return True
        else:
            return False


def judgeCircle(self, moves: str) -> bool:
        directions={'R':[1,0],'L':[-1,0],'U':[0,-1],'D':[0,1]}
        position=[0,0]
        for move in moves:
            position[0]+=directions[move][0]
            position[1]+=directions[move][1]
        return position==[0,0]


def judgeCircle(self, moves: str) -> bool:
    match = {'L': complex(-1, 0), 'R':complex(1, 0), 
             'D': complex(0, -1), 'U':complex(0, 1)}
    return not sum([match[step] for step in moves])



#
class Solution:
    def judgeCircle(self, moves: str) -> bool:
        robot = Robot()
        for i in moves:
            robot.move(i)
        return robot.x == 0 and robot.y == 0
class Robot():
    x = 0
    y = 0
    command = 'R L U D'.split()
    change = [(1,0), (-1, 0), (0, 1), (0, -1)]
    def move(self, string):
        '''string: a single string that represents the move of Robot'''
        index = self.command.index(string)
        self.x += self.change[index][0]
        self.y += self.change[index][1]












