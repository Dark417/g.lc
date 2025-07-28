# 547. 省份数量



def findCircleNum(self, isConnected: List[List[int]]) -> int:
    def dfs(i: int):
        for j in range(provinces):
            if isConnected[i][j] == 1 and j not in visited:
                visited.add(j)
                dfs(j)
    
    provinces = len(isConnected)
    visited = set()
    circles = 0

    for i in range(provinces):
        if i not in visited:
            dfs(i)
            circles += 1
    
    return circles


def findCircleNum(self, isConnected: List[List[int]]) -> int:
    provinces = len(isConnected)
    visited = set()
    circles = 0
    
    for i in range(provinces):
        if i not in visited:
            Q = collections.deque([i])
            while Q:
                j = Q.popleft()
                visited.add(j)
                for k in range(provinces):
                    if isConnected[j][k] == 1 and k not in visited:
                        Q.append(k)
            circles += 1
    
    return circles


def findCircleNum(self, isConnected: List[List[int]]) -> int:
    def find(index: int) -> int:
        if parent[index] != index:
            parent[index] = find(parent[index])
        return parent[index]
        
    def union(index1: int, index2: int):
        parent[find(index1)] = find(index2)
    
    provinces = len(isConnected)
    parent = list(range(provinces))
    
    for i in range(provinces):
        for j in range(i + 1, provinces):
            if isConnected[i][j] == 1:
                union(i, j)
    
    circles = sum(parent[i] == i for i in range(provinces))
    return circles



class UnionFind:
    def __init__(self):
        self.father = {}
        self.num_of_sets = 0
    
    def find(self,x):
        root = x
        
        while self.father[root] != None:
            root = self.father[root]
        
        while x != root:
            original_father = self.father[x]
            self.father[x] = root
            x = original_father
        
        return root
    
    def merge(self,x,y):
        root_x,root_y = self.find(x),self.find(y)
        
        if root_x != root_y:
            self.father[root_x] = root_y
            self.num_of_sets -= 1
    
    def add(self,x):
        if x not in self.father:
            self.father[x] = None
            self.num_of_sets += 1

class Solution:
    def findCircleNum(self, M: List[List[int]]) -> int:
        uf = UnionFind()
        for i in range(len(M)):
            uf.add(i)
            for j in range(i):
                if M[i][j]:
                    uf.merge(i,j)
        
        return uf.num_of_sets









