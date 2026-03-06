"""
068.690. Employee Importance

You are given a data structure of employee information, which includes the employee's 
unique id, his importance value and his direct subordinates' id.

For example, employee 1 is the leader of employee 2, and employee 2 is the leader of 
employee 3. They have importance value 15, 10 and 5, respectively. Then employee 1 
has a data structure like [1, 15, [2]], and employee 2 has [2, 10, [3]], and employee 3 
has [3, 5, []]. Note that although employee 3 is also a subordinate of employee 1, the relationship is not direct.

Now given the employee information of a company, and an employee id, you need to return 
the total importance value of this employee and all his subordinates.

Example 1:

Input: [[1, 5, [2, 3]], [2, 3, []], [3, 3, []]], 1
Output: 11
Explanation:
Employee 1 has importance value 5, and he has two direct subordinates: employee 2 and 
employee 3. They both have importance value 3. So the total importance value of employee 1 is 5 + 3 + 3 = 11.
 

Note:

One employee has at most one direct leader and may have several subordinates.
The maximum number of employees won't exceed 2000.

"""


def getImportance(self, employees: List['Employee'], id: int) -> int:
    pri = 0
    dic = {}
    for p in employees:
        dic[p.id] = p
    cur = [dic[id]]
    while cur:
        e = cur.pop(0)
        pri += e.importance
        cur.extend([dic[p] for p in e.subordinates])
    return pri

# official

# dfs
def getImportance(self, employees, query_id):
    emap = {e.id: e for e in employees}
    def dfs(eid):
        employee = emap[eid]
        return (employee.importance +
                sum(dfs(eid) for eid in employee.subordinates))
    return dfs(query_id)


    def dfs(self,hashmap,id):
        e=hashmap[id]
        res=e.importance
        for i in e.subordinates:
            res+=self.dfs(hashmap,i)
        return res

# bfs
def getImportance(self, employees: List['Employee'], id: int) -> int:
    hashmap = {e.id: e for e in employees}
    queue=[id]
    while queue:
        cur=queue.pop(0)
        e=hashmap[cur]
        res+=e.importance
        for i in e.subordinates:
            queue.append(i)
    return res


# recursion
class Employee:
    def __init__(self, id, importance, subordinates):
        # It's the unique id of each node.
        # unique id of this employee
        self.id = id
        # the importance value of this employee
        self.importance = importance
        # the id of direct subordinates
        self.subordinates = subordinates


#
def getImportance(self, employees, id):
    # Time: O(n)
    # Space: O(n)
    emps = {employee.id: employee for employee in employees}
    dfs = lambda id: sum([dfs(sub_id) for sub_id in emps[id].subordinates]) + emps[id].importance
    return dfs(id)    

def getImportance(self, employees, id):
    # Time: O(n)
    # Space: O(n)
    emps = {employee.id: employee for employee in employees}
    def dfs(id):
        subordinates_importance = sum([dfs(sub_id) for sub_id in emps[id].subordinates])
        return subordinates_importance + emps[id].importance
    return dfs(id)

def getImportance(self, employees, query_id):
    emap = {e.id: e for e in employees}
    def dfs(eid):
        employee = emap[eid]
        return (employee.importance +
                sum(dfs(eid) for eid in employee.subordinates))
    return dfs(query_id)

def getImportance(self, employees: List['Employee'], id: int) -> int:
    get_ipt = lambda i: dt[i].importance + sum(get_ipt(j) for j in dt[i].subordinates)
    dt = {e.id: e for e in employees}  
    return get_ipt(id)

def getImportance(self, employees: List['Employee'], id: int) -> int:
    get_ipt = lambda i, dt: dt[i].importance + sum(get_ipt(j, dt) for j in dt[i].subordinates)
    dt = {e.id: e for e in employees}  
    return get_ipt(id, dt)




class Solution:

    def __init__(self):
        self.hash_map = dict()
        self.visited = set()
        self.res = 0

    def getImportance(self, employees, id):
        for employee in employees:
            self.hash_map[employee.id] = employee
        self.__dfs(self.hash_map[id])
        return self.res

    def __dfs(self, employee):
        if employee.id in self.visited:
            return

        self.visited.add(employee.id)
        self.res += employee.importance

        for id in employee.subordinates:
            self.__dfs(self.hash_map[id])


# stack non-recursive
def getImportance(self, employees, id):
    hash_map = dict()
    for employee in employees:
        hash_map[employee.id] = employee

    res = 0
    visited = set()

    stack = [id]
    while stack:
        top = stack.pop()
        visited.add(top)
        res += hash_map[top].importance

        for subordinate_id in hash_map[top].subordinates:
            # 如果没有访问过，才添加到栈中
            if subordinate_id in visited:
                continue
            stack.append(subordinate_id)
    return res


# bfs
def getImportance(self, employees, id):
    hash_map = dict()
    for employee in employees:
        hash_map[employee.id] = employee

    res = 0
    queue = deque()
    queue.append(id)
    while queue:
        top = queue.popleft()
        res += hash_map[top].importance
        for subordinate_id in hash_map[top].subordinates:
            queue.append(subordinate_id)
    return res



def getImportance(self, employees, id):
    id_to_emp = {employee.id: employee for employee in employees}
    importance = 0
    stack = [id_to_emp[id]]
    while stack:
        cur_emp = stack.pop()
        importance += cur_emp.importance
        stack.extend([id_to_emp[new_emp] for new_emp in cur_emp.subordinates])
    return importance 























