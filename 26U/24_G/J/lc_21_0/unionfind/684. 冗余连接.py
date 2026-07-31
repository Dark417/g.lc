# 684. 冗余连接


def findRedundantConnection(self, edges):
    graph = collections.defaultdict(set)

    def dfs(source, target):
        if source not in seen:
            seen.add(source)
            if source == target: return True
            return any(dfs(nei, target) for nei in graph[source])

    for u, v in edges:
        seen = set()
        if u in graph and v in graph and dfs(u, v):
            return u, v
        graph[u].add(v)
        graph[v].add(u)


            
def findRedundantConnection(self, edges: List[List[int]]) -> List[int]:
    nodesCount = len(edges)
    parent = list(range(nodesCount + 1))

    def find(index: int) -> int:
        if parent[index] != index:
            parent[index] = find(parent[index])
        return parent[index]
    
    def union(index1: int, index2: int):
        parent[find(index1)] = find(index2)

    for node1, node2 in edges:
        if find(node1) != find(node2):
            union(node1, node2)
        else:
            return [node1, node2]
    
    return []










