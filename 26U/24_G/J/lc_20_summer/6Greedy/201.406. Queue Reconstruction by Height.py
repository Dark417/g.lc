"""
201.406. Queue Reconstruction by Height

Suppose you have a random list of people standing in a queue. Each person is described 
by a pair of integers (h, k), where h is the height of the person and k is the number 
of people in front of this person who have a height greater than or equal to h. Write 
an algorithm to reconstruct the queue.

Note:
The number of people is less than 1,100.

 
Example

Input:
[[7,0], [4,4], [7,1], [5,0], [6,1], [5,2]]

Output:
[[5,0], [7,0], [5,2], [6,1], [4,4], [7,1]]


"""


# official
def reconstructQueue(self, people: List[List[int]]) -> List[List[int]]:
    people.sort(key = lambda x: (-x[0], x[1]))
    output = []
    for p in people:
        output.insert(p[1], p)
    return output



	res = []
    for p in sorted((-x[0], x[1]) for x in people):
        res.insert(p[1], [-p[0], p[1]])
    return res




def reconstructQueue(self, people):
    hp = []
    for p in people:
        heapq.heappush(hp, (-p[0],p[1]))
    ans = []
    while hp:
        p = heapq.heappop(hp)
        ans.insert(p[1], [-p[0],p[1]])
    return ans




def reconstructQueue(self, people: List[List[int]]) -> List[List[int]]:
    people.sort(key=lambda x: (x[0], -x[1])) 
    ans = [None]*len(people)
    idx = list(range(len(people)))
    
    for p in people:
        ans[idx.pop(p[1])] = p
    return ans 



def reconstructQueue(self, people):    N = len(people)
    results = [0] * N
    positions = list(range(N))
    fn = lambda person: (person[0], -person[1])
    for h, k in sorted(people, key=fn):
        i = positions.pop(k)
        results[i] = [h, k]
    return results



def reconstructQueue(self, people):
        """
		[ ] [ ] [ ] [ ] [4] [ ]    #  [4, 4]: 6 slots, insert 4 with 4 empty space before it
		[5] [ ] [ ] [ ]     [ ]    #  [5, 0]: 5 slots, insert 5 with 0 empty space before it
		    [ ] [5] [ ]     [ ]    #  [5, 2 - 1]: 4 slots, insert 5 with 1 empty space before it
		    [ ]     [6]     [ ]    #  [6, 1]: 3 slots, insert 6 with 1 empty space before it
			[7]             [ ]    #  [7, 0]: 2 slots, insert 7 with 0 empty space before it
			                [7]    #  [7, 1 - 1]: 1 slots, insert 7 with 0 empty space before it
        """
        people = sorted(people)
        rst = [None] * len(people)
        same_before = 0
        for i, (h, c) in enumerate(people):
            if i > 0 and h == people[i - 1][0]:
                same_before += 1
            elif i > 0 and h != people[i - 1][0]:
                same_before = 0
			# find this person's correct position
            idx, empty = 0, 0
            while empty <= c - same_before:
                if rst[idx] is None:
                    empty += 1
                idx += 1
            rst[idx - 1] = [h, c]
        return rst





# https://leetcode.com/problems/queue-reconstruction-by-height/discuss/89367/O(n-sqrt(n))-solution
# O(n)
def reconstructQueue(self, people):
    blocks = [[]]
    for p in sorted(people, key=lambda (h, t): (-h, t)):
        index = p[1]

        for i, block in enumerate(blocks):
            m = len(block)
            if index <= m:
                break
            index -= m
        block.insert(index, p)
        if m * m > len(people):
            blocks.insert(i + 1, block[m/2:])
            del block[m/2:]

    return [p for block in blocks for p in block]





def reconstructQueue(self, people):
    if not people: return []

    # obtain everyone's info
    # key=height, value=k-value, index in original array
    peopledct, height, res = {}, [], []
    
    for i in xrange(len(people)):
        p = people[i]
        if p[0] in peopledct:
            peopledct[p[0]] += (p[1], i),
        else:
            peopledct[p[0]] = [(p[1], i)]
            height += p[0],

    height.sort()      # here are different heights we have

    # sort from the tallest group
    for h in height[::-1]:
        peopledct[h].sort()
        for p in peopledct[h]:
            res.insert(p[0], people[p[1]])

    return res


# https://leetcode.com/problems/queue-reconstruction-by-height/discuss/673129/Python-O(n2)-easy-to-come-up-detailed-explanations




def reconstructQueue(self, people: List[List[int]]) -> List[List[int]]:
    people = [[x, y, y] for x, y in people]
    for i in range(len(people) - 1):
        ind = people.index(min(people[i:] ,key=lambda x: (x[2], x[0])))
        people[i], people[ind] = people[ind], people[i]
        people = [[x, y, z - (x <= people[i][0])] for x, y, z in people]
    return [[x, y] for x, y, z in people]





































































