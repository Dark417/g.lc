# 323. 无向图中连通分量的数目


class UnionFind:
    def __init__(self, n):
        self.n = n
        self.part = n
        self.parent = [x for x in range(n)]
        self.size = [1 for _ in range(n)]

    def Find(self, x: int) -> int:
        if self.parent[x] == x:
            return x
        return self.Find(self.parent[x])

    def Union(self, x: int, y: int) -> bool:
        root_x = self.Find(x)
        root_y = self.Find(y)
        if root_x == root_y:
            return False
        if self.size[root_x] > self.size[root_y]:
            root_x, root_y = root_y, root_x
        self.parent[root_x] = root_y
        self.size[root_y] += self.size[root_x]
        self.part -= 1
        return True
    
    def in_the_same_part(self, x: int, y: int) -> bool:
        return self.Find(x) == self.Find(y)
    
    def get_part_size(self, x: int) -> int:
        root_x = self.Find(x)
        return self.size[root_x]

class Solution:
    def countComponents(self, n: int, edges: List[List[int]]) -> int:
        UF = UnionFind(n)
        for x, y in edges:
            UF.Union(x, y)
        return UF.part
































