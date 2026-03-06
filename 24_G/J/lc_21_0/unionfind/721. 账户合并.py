# 721. 账户合并

def accountsMerge(self, accounts):
    from collections import defaultdict

    f = {}

    def find(x):
        f.setdefault(x, x)
        while f[x] != x:
            #x = f[x]
            f[x] = f[f[x]]
            x = f[x]
        return x

    def union(x, y):
        f[find(x)] = find(y)

    lookup = {}
    n = len(accounts)
    for idx, account in enumerate(accounts):
        name = account[0]
        email = account[1:]
        for e in email:
            if e in lookup:
                union(idx, lookup[e])
            else:
                lookup[e] = idx
    disjointSet = defaultdict(set)
    for i in range(n):
        tmp = find(i)
        for es in accounts[i][1:]:
            disjointSet[tmp].add(es)
    res = []
    for key, val in disjointSet.items():
        res.append([accounts[key][0]] + list(sorted(val)))
    return res 



# bfs

def accountsMerge(self, accounts):
    from collections import defaultdict, deque
    graph = defaultdict(set)
    email_to_name = defaultdict()
    for account in accounts:
        name = account[0]
        emails = account[1:]
        for email in emails:
            email_to_name[email] = name
            graph[emails[0]].add(email)
            graph[email].add(emails[0])
    visited = set()
    res = []

    def bfs(e):
        ans = []
        stack = deque()
        stack.appendleft(e)
        while stack:
            tmp = stack.pop()
            ans.append(tmp)
            for t in graph[tmp]:

                if t not in visited:
                    visited.add(t)
                    stack.appendleft(t)
        return ans

    for e in graph:
        if e not in visited:
            visited.add(e)
            ans = bfs(e)
            res.append([email_to_name[e]] + sorted(ans))
    return res


# dfs

def accountsMerge(self, accounts):
    from collections import defaultdict, deque
    graph = defaultdict(set)
    email_to_name = defaultdict()
    for account in accounts:
        name = account[0]
        emails = account[1:]
        for email in emails:
            email_to_name[email] = name
            graph[emails[0]].add(email)
            graph[email].add(emails[0])
    visited = set()
    res = []
    def dfs(e):
        new_list.append(e)
        for t in graph[e]:
            if t not in visited:
                visited.add(t)
                dfs(t)
    for e in graph:
        if e not in visited:
            visited.add(e)
            new_list = []
            dfs(e)
            res.append([email_to_name[e]] + sorted(new_list))
    return res



# 集合

    def accountsMerge(self, accounts):
        from collections import defaultdict
        if not accounts:
            return
        lookup = defaultdict(list)
        res = []
        for account in accounts:
            name = account[0]
            email = set(account[1:])

            lookup[name].append(email)
            for e in lookup[name][:-1]:
                if e & email:
                    lookup[name].remove(e)
                    lookup[name][-1].update(e)
        for key, val in lookup.items():

            for tmp in val:
                res.append([key] + list(sorted(tmp)))
        return res




class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def union(self, index1: int, index2: int):
        self.parent[self.find(index2)] = self.find(index1)

    def find(self, index: int) -> int:
        if self.parent[index] != index:
            self.parent[index] = self.find(self.parent[index])
        return self.parent[index]

class Solution:
    def accountsMerge(self, accounts: List[List[str]]) -> List[List[str]]:
        emailToIndex = dict()
        emailToName = dict()

        for account in accounts:
            name = account[0]
            for email in account[1:]:
                if email not in emailToIndex:
                    emailToIndex[email] = len(emailToIndex)
                    emailToName[email] = name
        
        uf = UnionFind(len(emailToIndex))
        for account in accounts:
            firstIndex = emailToIndex[account[1]]
            for email in account[2:]:
                uf.union(firstIndex, emailToIndex[email])
        
        indexToEmails = collections.defaultdict(list)
        for email, index in emailToIndex.items():
            index = uf.find(index)
            indexToEmails[index].append(email)
        
        ans = list()
        for emails in indexToEmails.values():
            ans.append([emailToName[emails[0]]] + sorted(emails))
        return ans



class Solution:
    class UnionFind:
        def __init__(self, n):
            self.parent = list(range(n))
            self.rank = [1] * n

        def find(self, x):
            if x != self.parent[x]:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]

        def union(self, x, y):
            root_x = self.find(x)
            root_y = self.find(y)
            if root_x == root_y:
                return
            if self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            elif self.rank[root_x] > self.rank[root_y]:
                self.parent[root_y] = root_x
            else:
                self.parent[root_y] = root_x
                self.rank[root_x] += 1

    def accountsMerge(self, accounts: List[List[str]]) -> List[List[str]]:
        uf = Solution.UnionFind(len(accounts))
        email_id = dict()  # key: email, value: id (index)
        # key: id (index), value: email list
        id_email = collections.defaultdict(list)

        for i, a in enumerate(accounts):
            for e in a[1:]:
                if e in email_id:
                    uf.union(email_id[e], i)
                else:
                    email_id[e] = i

        for e, i in email_id.items():
            id_email[uf.find(i)].append(e)  # 注意这里id_email的key

        return [[accounts[i][0]] + sorted(e) for i, e in id_email.items()]





























