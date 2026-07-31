"""
181.56. Merge Intervals
合并区间

Given a collection of intervals, merge all overlapping intervals.

Example 1:

Input: [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]
Explanation: Since intervals [1,3] and [2,6] overlaps, merge them into [1,6].
Example 2:

Input: [[1,4],[4,5]]
Output: [[1,5]]
Explanation: Intervals [1,4] and [4,5] are considered overlapping.
NOTE: input types have been changed on April 15, 2019. Please reset to default code 
definition to get new method signature.

https://leetcode-cn.com/problems/merge-intervals/solution/na-kong-jian-huan-shi-jian-er-qie-wo-mei-pai-xu-_-/
计数排序
counting sort

"""

def merge(self, intervals: List[List[int]]) -> List[List[int]]:
    i = 0
    intervals.sort(key = lambda x: x[0])
    while i < len(intervals)-1:
        if intervals[i][1] >= intervals[i+1][0]:
            if intervals[i][1] <= intervals[i+1][1]:
                intervals[i] = [intervals[i][0], intervals[i+1][1]]
            intervals.pop(i+1)
        else:
            i += 1
    return intervals


def merge(self, intervals):
    out = []
    for i in sorted(intervals, key=lambda i: i.start):
        if out and i.start <= out[-1].end:
            out[-1].end = max(out[-1].end, i.end)
        else:
            out += i
    return out


def merge(self, intervals):
    if len(intervals) == 0: return []
    intervals = sorted(intervals, key = lambda x: x.start)
    res = [intervals[0]]
    for n in intervals[1:]:
        if n.start <= res[-1].end: res[-1].end = max(n.end, res[-1].end)
        else: res.append(n)
    return res


# official

def merge(self, intervals: List[List[int]]) -> List[List[int]]:
    intervals.sort(key=lambda x: x[0])
    merged = []
    for interval in intervals:
        # 如果列表为空，或者当前区间与上一区间不重合，直接添加
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)
        else:
            # 否则的话，我们就可以与上一区间进行合并
            merged[-1][1] = max(merged[-1][1], interval[1])

    return merged


# e
def overlap(self, a, b):
    return a[0] <= b[1] and b[0] <= a[1]

# generate graph where there is an undirected edge between intervals u
# and v iff u and v overlap.
def build_graph(self, intervals):
    graph = collections.defaultdict(list)

    for i, interval_i in enumerate(intervals):
        for j in range(i+1, len(intervals)):
            if self.overlap(interval_i, intervals[j]):
                graph[tuple(interval_i)].append(intervals[j])
                graph[tuple(intervals[j])].append(interval_i)

    return graph

# merges all of the nodes in this connected component into one interval.
def merge_nodes(self, nodes):
    min_start = min(node[0] for node in nodes)
    max_end = max(node[1] for node in nodes)
    return [min_start, max_end]

# gets the connected components of the interval overlap graph.
def get_components(self, graph, intervals):
    visited = set()
    comp_number = 0
    nodes_in_comp = collections.defaultdict(list)

    def mark_component_dfs(start):
        stack = [start]
        while stack:
            node = tuple(stack.pop())
            if node not in visited:
                visited.add(node)
                nodes_in_comp[comp_number].append(node)
                stack.extend(graph[node])

    # mark all nodes in the same connected component with the same integer.
    for interval in intervals:
        if tuple(interval) not in visited:
            mark_component_dfs(interval)
            comp_number += 1

    return nodes_in_comp, comp_number


def merge(self, intervals: List[List[int]]) -> List[List[int]]:
    graph = self.build_graph(intervals)
    nodes_in_comp, number_of_comps = self.get_components(graph, intervals)

    # all intervals in each connected component must be merged.
    return [self.merge_nodes(nodes_in_comp[comp]) for comp in range(number_of_comps)]



"""
public int[][] merge(int[][] intervals) {
        // 先按照区间起始位置排序
        Arrays.sort(intervals, (v1, v2) -> v1[0] - v2[0]);
        // 遍历区间
        int[][] res = new int[intervals.length][2];
        int idx = -1;
        for (int[] interval: intervals) {
            // 如果结果数组是空的，或者当前区间的起始位置 > 结果数组中最后区间的终止位置，
            // 则不合并，直接将当前区间加入结果数组。
            if (idx == -1 || interval[0] > res[idx][1]) {
                res[++idx] = interval;
            } else {
                // 反之将当前区间合并至结果数组的最后区间
                res[idx][1] = Math.max(res[idx][1], interval[1]);
            }
        }
        return Arrays.copyOf(res, idx + 1);
    }

"""







































































