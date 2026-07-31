"""
158.1351. Count Negative Numbers in a Sorted Matrix
统计有序矩阵中的负数

Given a m * n matrix grid which is sorted in non-increasing order both row-wise and column-wise. 

Return the number of negative numbers in grid.

 

Example 1:

Input: grid = [[4,3,2,-1],[3,2,1,-1],[1,1,-1,-2],[-1,-1,-2,-3]]
Output: 8
Explanation: There are 8 negatives number in the matrix.
Example 2:

Input: grid = [[3,2],[1,0]]
Output: 0
Example 3:

Input: grid = [[1,-1],[-1,-1]]
Output: 3
Example 4:

Input: grid = [[-1]]
Output: 1
 

Constraints:

m == grid.length
n == grid[i].length
1 <= m, n <= 100
-100 <= grid[i][j] <= 100


"""



def countNegatives(self, grid: List[List[int]]) -> int:
    return sum(i < 0 for j in grid for i in j )


    return str(grid).count('-')

    
return sum(bisect_left(type('', (), {'__getitem__': lambda _, i: r[~i]})(), 0, 0, len(r)) for r in A)

return(j:=0)or sum((j:=next((j for j in range(j,len(r))if r[~j]>=0),len(r)))for r in A)
return sum(itertools.accumulate([0]+A,lambda j,r:next((j for j in range(j,len(r))if r[~j]>=0),len(r))))



def countNegatives(self, A) -> int:
    class Lazy:
        def __init__(self, row):
            self.row = row
        def __getitem__(self, i):
            return self.row[len(self.row) - i - 1]
    return sum(map(lambda x: bisect_left(Lazy(x), 0, 0, len(x)), A))


"""
public:
    int solve(int l,int r,int L,int R,vector<vector<int> > grid){
        if (l>r) return 0;
        int mid=l+((r-l)>>1),pos=-1;
        for (int i=L;i<=R;++i){
            if (grid[mid][i]<0){
                pos=i;
                break;
            }
        }
        int ans=0;
        if (~pos){
            ans+=(int)grid[0].size()-pos;
            ans+=solve(l,mid-1,pos,R,grid);
            ans+=solve(mid+1,r,L,pos,grid);
        }
        else{// 说明[l..o-1]不会有负数，不用再去递归
            ans+=solve(mid+1,r,L,R,grid);
        }
        return ans;
    }
    int countNegatives(vector<vector<int>>& grid) {
        return solve(0,(int)grid.size()-1,0,(int)grid[0].size()-1,grid);
    }



"""

def countNegatives(self, grid):
    def bin(row):
        start, end = 0, len(row)
        while start<end:
            mid = start +(end -start) // 2
            if row[mid]<0:
                end = mid
            else:
                start = mid+1
        return len(row)- start
    
    count = 0
    for row in grid:
        count += bin(row)
    return(count)



def countNegatives(self, grid: List[List[int]]) -> int:
    l = len(grid[-1])
    def countNeg(start, end, a):
        if start > end:
            return 0
        mid = start + (end - start) // 2
        if a[mid] >= 0 > a[mid + 1]:
            return l - mid - 1
        elif a[mid] >= 0: 
            return countNeg(mid + 1, end, a)
        # else in left subarray
        elif a[mid] < 0:
            return countNeg(start, mid - 1, a)
    res = 0
    for a in grid:
        if a[0] < 0: # if the first element is negative, the rest will be too
            res += l
            continue
        elif a[-1] >= 0: # if the last element is positive, the previous was positives too
            continue
        res += countNeg(0, l - 1, a)
    return res




def countNegatives(self, grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    r, c, cnt = m - 1, 0, 0
    while r >= 0 and c < n:
        if grid[r][c] < 0:
            cnt += n - c
            r -= 1
        else:
            c += 1
    return cnt


def countNegatives(self, grid):
    i = len(grid)-1
    j = 0
    count = 0
    while i>=0 and j< len(grid[0]):
        if grid[i][j] < 0:
            count +=len(grid[0])-j
            i -= 1
        else:
            j +=1
    return(count)




# memoized for + bin
def countNegatives(self, grid: List[List[int]]) -> int:
    def binary_search(row: List[int], start: int, end: int) -> int:
        if start > end:
            return 0
        mid = (start + end) // 2
        if row[mid] >= 0:
            if mid < end and row[mid + 1] < 0:
                return end - mid
            return binary_search(row, mid + 1, end)
        else:
            if mid > start and row[mid - 1] >= 0:
                return end - mid + 1
            return (end - mid + 1) + binary_search(row, start, mid - 1)
    result = []
    for row in grid:
        if result == []:
            result.append(binary_search(row, 0, len(row) - 1))
        else:
            # use the previous result since current row will have
            # negative numbers count >= previous one
            # and set binary search boundaries accordingly
            result.append(
                binary_search(row, 0, len(row) - result[-1] - 1) + result[-1]
            )
    return sum(result)





# for + bin
def countNegatives(self, grid: List[List[int]]) -> int:
    res = 0
    for arr in grid:
        l,r = 0,len(arr)
        if arr[0] < 0:
            res += r
        elif arr[r-1] >= 0:
            continue
        else:
            while l < r:
                mid = (l+r)//2
                if arr[mid] < 0:
                    r = mid
                elif arr[mid] >= 0:
                    l = mid+1
            res += len(arr)-r
    return res



def countNegatives(self, grid: List[List[int]]) -> int:
    def bin(row):
        l,h=0,len(row)
        while (l<h):
            m=(l+h)//2
            if (row[m] <0):
                h=m
            elif (g[m]>=0):
                l=m+1
        return len(row)-h
    count=0
    for g in grid:
        count=count+bin(g)
    return count



def countNegatives(self, grid: List[List[int]]) -> int:
    count = 0
    for arr in grid:
        #the last element is positive or zero, so skip the array
        if arr[-1]>=0:
            continue
        #the first element is negative, so will be the whole array
        elif arr[0]<0:
            count += len(arr)
        else:
            #otherwise, perform binary search
            count += self.binary_search(arr, 0, len(arr)-1)
    return count

def binary_search(self, arr: List[int], l:int, r:int) -> int: 
    if r >= l: 

        mid = l + (r - l) // 2
        #if arr[mid] is negative, so will be the following elements
        #just in case you missed some negative numbers on the left half, conduct a binary search on it as well
        if arr[mid] <0:
            return (r-mid+1) + self.binary_search(arr, l, mid-1)
        #if arr[mid]>=0, all numbers in the left half will either be positive or zero,
        #so skip that and check the right half
        else: 
            return self.binary_search(arr, mid + 1, r) 

    else: 
        return 0



def countNegatives(self, grid: List[List[int]]) -> int:
    l = len(grid[-1])
    
    def countNeg(start, end, a):
        # base case
        if start > end:
            return 0
        
        mid = start + (end - start) // 2
        
        # found positive, negative element
        if a[mid] >= 0 > a[mid + 1]:
            return l - mid - 1

        # if element is greather or equal than 0, then
        # it can only be present in right subarray
        elif a[mid] >= 0: 
            return countNeg(mid + 1, end, a)
        # else in left subarray
        elif a[mid] < 0:
            return countNeg(start, mid - 1, a)
    res = 0
    for a in grid:
        if a[0] < 0: # if the first element is negative, the rest will be too
            res += l
            continue
        elif a[-1] >= 0: # if the last element is positive, the previous was positives too
            continue
        res += countNeg(0, l - 1, a)
    return res



def countNegatives(self, grid: List[List[int]]) -> int:
    l = len(grid[-1])
    
    def countNeg(start, end, a):
        # base case
        if start > end:
            return 0
        
        mid = start + (end - start) // 2
        
        # found positive, negative element
        if a[mid] >= 0 > a[mid + 1]:
            return l - mid - 1

        # if element is greather or equal than 0, then
        # it can only be present in right subarray
        elif a[mid] >= 0: 
            return countNeg(mid + 1, end, a)
        # else in left subarray
        elif a[mid] < 0:
            return countNeg(start, mid - 1, a)
    res = 0
    for a in grid:
        if a[0] < 0: # if the first element is negative, the rest will be too
            res += l
            continue
        elif a[-1] >= 0: # if the last element is positive, the previous was positives too
            continue
        res += countNeg(0, l - 1, a)
    return res





































































































