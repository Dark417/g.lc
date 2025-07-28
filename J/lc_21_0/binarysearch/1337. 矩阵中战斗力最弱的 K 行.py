# 1337. 矩阵中战斗力最弱的 K 行


def kWeakestRows(self, mat: List[List[int]], k: int) -> List[int]:
    n = len(mat)
    power = [sum(line) for line in mat]
    ans = list(range(n))
    ans.sort(key=lambda i: (power[i], i))
    return ans[:k]

# 如果第一个power[i]有相同，就按照第二个i来排



def kWeakestRows(self, mat: List[List[int]], k: int) -> List[int]:
    m,n=len(mat),len(mat[0])
    h=[]
    for i in range(m):
        #二分查找最左边的0
        left,right=0,n-1
        while left<right:
            mid=left+((right-left)>>1)
            if mat[i][mid]==1:
                left=mid+1
            else:
                right=mid
        if mat[i][left]==1:
            left+=1
        heapq.heappush(h,[left,i])
    weakest_K=heapq.nsmallest(k,h)
    return [item[1] for item in weakest_K]









































