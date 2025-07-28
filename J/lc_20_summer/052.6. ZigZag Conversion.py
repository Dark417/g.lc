"""
052.6. ZigZag Conversion 
Z 字形变换


The string "PAYPALISHIRING" is written in a zigzag pattern on a given number of rows like this: (you may want to display this pattern in a fixed font for better legibility)

P   A   H   N
A P L S I I G
Y   I   R
And then read line by line: "PAHNAPLSIIGYIR"

Write the code that will take a string and make this conversion given a number of rows:

string convert(string s, int numRows);
Example 1:

Input: s = "PAYPALISHIRING", numRows = 3
Output: "PAHNAPLSIIGYIR"
Example 2:

Input: s = "PAYPALISHIRING", numRows = 4
Output: "PINALSIGYAHRPI"
Explanation:

P     I    N
A   L S  I G
Y A   H R
P     I

"""

def convert(self, s: str, numRows: int) -> str:
    if len(s) == 0: return ""
    if numRows == 1: return s 
    l = [""] * numRows
    row = 0
    dir = 1
    i = 0
    while i < len(s):
        if dir == 1:
            if row < numRows-1:
                l[row] += s[i]
                row += 1
            else:
                l[row] += s[i]
                dir = 2
        else:
            row -= 1
            if row != 0:
                l[row] += s[i]
            else:
                dir = 1
                i -= 1
        i += 1
    return "".join(l)


def convert(self, s: str, numRows: int) -> str:
    if numRows < 2: return s
    res = ["" for _ in range(numRows)]
    i, flag = 0, -1
    for c in s:
        res[i] += c
        if i == 0 or i == numRows - 1: flag = -flag
        i += flag
    return "".join(res)


def convert(self, s, numRows):
    if numRows == 1 or numRows >= len(s):
        return s
    L = [''] * numRows
    index, step = 0, 1

    for x in s:
        L[index] += x
        if index == 0:
            step = 1
        elif index == numRows -1:
            step = -1
        index += step
    return ''.join(L)


def convert(self, s, numRows):
    if numRows == 1 or numRows >= len(s):
        return s
    # This is a vague sentence for python beginers
    L = [''] * numRows
    # it can be replaced by the following:
    # L = []
    # for i in range(0, numRows):
    #     L.append('')
    # so if numRows = 3, L = ['', '', '']
    index, step = 0, 1

    for x in s:
        L[index] += x
        #@1 start #
        if index == 0:
            step = 1
        elif index == numRows -1:
            step = -1
        #@1 end  #
        # I like to explain the part above
        # take the str "PAYPALISHIRING" for example:
        # We start with variable index with the value 0, step with the value 1
        # Each row added with the next char
        # If we reach the bottommost row, we need to turn to the next above row, so we change the step value to -1
        # we keep the step value until we reach topmost row. DON'T CHANGE IT!
        # Again, if we reach the topmost row, we need to reset the step value to 1
        # What we need to remember is:
        # the zigzag pattern is just a pictorial image for us to have a better understanding
        # What the trick of algorithm is actually add the next char of the given string to different rows.
        # Don't really think how to move the cursor in the matrix.
        # It's really misleading way you think of this. Even it works, it's not efficient.
        index += step
    return ''.join(L)


def convert(self, s, numRows):
    step = (numRows == 1) - 1  # 0 or -1  
    rows, idx = [''] * numRows, 0
    for c in s:
        rows[idx] += c
        if idx == 0 or idx == numRows-1: 
            step = -step  #change direction  
        idx += step
    return ''.join(rows)


def convert(s, numRows):
    if numRows<2 or len(s)<numRows: return s
    rows = [""]*numRows
    ind, step = 0, 1
    for v in s:
        rows[ind] += v
        if ind == 0: step = 1
        elif ind == numRows-1: step = -1
        ind += step
    return ''.join(rows)


def convert2(s, numRows):
    if numRows<2 or len(s)<numRows: return s
    rows = [[] for _ in range(numRows)]
    ind, step = 0, 1
    for v in s:
        rows[ind] += v
        if ind == 0: step = 1
        elif ind == numRows-1: step = -1
        ind += step
    return ''.join(''.join(row) for row in rows)


def convert1(s, numRows):
    if numRows<2 or len(s)<numRows: return s
    n = numRows-1
    step = n*2
    res = s[::step]
    for i in range(1,n):
        for v,w in itertools.zip_longest(s[i::step],s[step-i::step],fillvalue=''):
            res += v+w
    return res + s[n::step]


def convert(self, S: str, R: int) -> str:
    if R == 1 or R > len(S):  # corner case
        return S
    res, i, step = ['' for r in range(R)], 0, 0  # a string for each line
    for s in S:
        res[i] += s
        if i == 0:  # first row
            step = 1  # down
        if i == R - 1:  # last row
            step = -1  # up
        i += step
    return "".join(res)













