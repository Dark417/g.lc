"""
175.118. Pascal's Triangle
杨辉三角

Given a non-negative integer numRows, generate the first numRows of Pascal's triangle.


In Pascal's triangle, each number is the sum of the two numbers directly above it.

Example:

Input: 5
Output:
[
     [1],
    [1,1],
   [1,2,1],
  [1,3,3,1],
 [1,4,6,4,1]
]

"""








def generate(self, numRows: int) -> List[List[int]]:
    res = [[1]]
    for _ in range(numRows-1):
        o = res[-1]
        n = [0] * len(o) + [1]
        n[0] = n[-1] = 1
        for i in range(1, len(n)-1):
            n[i] = o[i-1] + o[i]
        res.append(n)
    return res





def generate(self, numRows: int) -> List[List[int]]:
    if numRows == 0: return []
    res = [[1]]
    while len(res) < numRows:
        newRow = [a+b for a, b in zip([0]+res[-1], res[-1]+[0])]
        res.append(newRow)      
    return res


def generate(self, numRows):
    res = [[1]]
    for i in range(1, numRows):
        res += [map(lambda x, y: x+y, res[-1] + [0], [0] + res[-1])]
    return res[:numRows]




def generate(self, numRows):
    res = [[1]]
    for _ in range(1, numRows):
        map_ = map(add, [0] + res[-1], res[-1] + [0])
        res.append(list(map_))
    return res if numRows else []




def generate(numRows):
    pascal = [[1]*(i+1) for i in range(numRows)]
    for i in range(numRows):
        for j in range(1,i):
            pascal[i][j] = pascal[i-1][j-1] + pascal[i-1][j]
    return pascal




def generate(self, numRows):
    lists = []
    for i in range(numRows):
        lists.append([1]*(i+1))
        if i>1 :
            for j in range(1,i):
                lists[i][j]=lists[i-1][j-1]+lists[i-1][j]
    return lists



def generate(self, numRows):
    n,b,res=0,[1],[]
    while n<numRows:
        res.append(b)
        b=[1]+[b[i]+b[i+1] for i in xrange(len(b)-1)]+[1]
        n+=1
    return res



def generate(self, numRows: int) -> List[List[int]]:
    ret = list()
    for i in range(numRows):
        row = list()
        for j in range(0, i + 1):
            if j == 0 or j == i:
                row.append(1)
            else:
                row.append(ret[i - 1][j] + ret[i - 1][j - 1])
        ret.append(row)
    return ret



























































