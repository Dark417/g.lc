"""
126.437. Path Sum III


You are given a binary tree in which each node contains an integer value.

Find the number of paths that sum to a given value.

The path does not need to start or end at the root or a leaf, but it must go 
downwards (traveling only from parent nodes to child nodes).

The tree has no more than 1,000 nodes and the values are in the range -1,000,000 to 1,000,000.

Example:

root = [10,5,-3,3,2,null,11,3,-2,null,1], sum = 8

      10
     /  \
    5   -3
   / \    \
  3   2   11
 / \   \
3  -2   1

Return 3. The paths that sum to 8 are:

1.  5 -> 3
2.  5 -> 2 -> 1
3. -3 -> 11
"""

def pathSum(self, root: TreeNode, sum: int) -> int:
    res = 0
    def dfs(node, cur):
        if cur == sum:
            res += 1
         



        if not node.left and not node.right:
        

    dfs(root, 0)
    return 



def pathSum(self, root: TreeNode, sum: int) -> int:
    if not root: return 0
    res = 0
    cur = [(root, root.val)]
    while cur:
        node, s = cur.pop(0)
        if s == sum:
            res += 1
        else:
            if node.left:
                cur.append((node.left, s+node.left.val))
                cur.append((node.left, node.left.val))
            if node.right:
                cur.append((node.right, s+node.right.val))
                cur.append((node.right, node.right.val))
    return res 




# 精简版，五行代码不解释
def pathSum(self, root: TreeNode, sum: int) -> int:
    def dfs(root, sumlist):
        if root is None: return 0
        sumlist = [num + root.val for num in sumlist] + [root.val]
        return sumlist.count(sum) + dfs(root.left, sumlist) + dfs(root.right, sumlist)
    return dfs(root, [])


# 展开版，易理解
def pathSum(self, root: TreeNode, sum: int) -> int:

    def dfs(root, sumlist):
        if root is None:
            return 0
        sumlist = [num+root.val for num in sumlist]
        sumlist.append(root.val)
        count = 0
        for num in sumlist:
            if num == sum:
                count += 1
        # count = sumlist.count(sum)
        return count + dfs(root.left, sumlist) + dfs(root.right, sumlist)
    return dfs(root, [])




def pathSum(self, root: TreeNode, sum: int) -> int:
	cnt = 0
    def dfs(root, start, s):
        if not root:
            return
        s -= root.val 
        if s==0:
            self.cnt+=1
        dfs(root.left,False, s)
        dfs(root.right,False, s)
        if start: 
            dfs(root.left,True,sum)
            dfs(root.right,True,sum)
    
    dfs(root, True, sum)
    return self.cnt



def pathSum(self, root: TreeNode, sum: int) -> int:
    sum=[sum]
    count=[0]
    def bfs(root,sums):
        if not root:
            return
        sums=[sum+root.val for sum in sums]+[root.val]
        count[0]+=sums.count(sum[0])
        bfs(root.left,sums)
        bfs(root.right,sums)
    bfs(root,[])
    return count[0]



def pathSum(self, root, target):
        # define global return var
        self.numOfPaths = 0
        # 1st layer DFS to go through each node
        self.dfs(root, target)
        # return result
        return self.numOfPaths
    
    # define: traverse through the tree, at each treenode, call another DFS to test if a path sum include the answer
    def dfs(self, node, target):
        # exit condition
        if node is None:
            return 
        # dfs break down 
        self.test(node, target) # you can move the line to any order, here is pre-order
        self.dfs(node.left, target)
        self.dfs(node.right, target)
        
    # define: for a given node, DFS to find any path that sum == target, if find self.numOfPaths += 1
    def test(self, node, target):
        # exit condition
        if node is None:
            return
        if node.val == target:
            self.numOfPaths += 1
            
        # test break down
        self.test(node.left, target-node.val)
        self.test(node.right, target-node.val)



def pathSum(self, root, target):
    # define global result and path
    self.result = 0
    cache = {0:1}
    
    # recursive to get result
    self.dfs(root, target, 0, cache)
    
    # return result
    return self.result

def dfs(self, root, target, currPathSum, cache):
    # exit condition
    if root is None:
        return  
    # calculate currPathSum and required oldPathSum
    currPathSum += root.val
    oldPathSum = currPathSum - target
    # update result and cache
    self.result += cache.get(oldPathSum, 0)
    cache[currPathSum] = cache.get(currPathSum, 0) + 1
    
    # dfs breakdown
    self.dfs(root.left, target, currPathSum, cache)
    self.dfs(root.right, target, currPathSum, cache)
    # when move to a different branch, the currPathSum is no longer available, hence remove one. 
    cache[currPathSum] -= 1



def pathSum(self, root, sum):
    def dfs(root, prevSum, sum):
        if not root:
            return 
        currSum = prevSum + root.val
        if currSum - sum in rec:
            self.count += rec[currSum - sum]
        if currSum in rec:
            rec[currSum] += 1
        else:
            rec[currSum] = 1
        dfs(root.left, currSum, sum)
        dfs(root.right, currSum, sum)
        rec[currSum] -= 1
        
    self.count = 0
    rec = {0:1}
    dfs(root, 0, sum)
    return self.count



def pathSum(self, root, sum):
    def dfs(root, prevSum, sum):
        if not root:
            return 0
        count = 0
        currSum = prevSum + root.val
        if currSum - sum in rec:
            count += rec[currSum - sum]
        if currSum in rec:
            rec[currSum] += 1
        else:
            rec[currSum] = 1
        count += dfs(root.left, currSum, sum)
        count += dfs(root.right, currSum, sum)
        rec[currSum] -= 1
        return count
        
    rec = {0:1}
    return dfs(root, 0, sum)








def dfs(self, node, store, pathSum, sum):
    pathSum += node.val
    if pathSum - sum in store:
        self.count += store[pathSum- sum]
    if pathSum == sum:
        self.count += 1
    if pathSum in store:
        store[pathSum] += 1
    else:
        store[pathSum] = 1
    if node.left:
        self.dfs(node.left, store, pathSum, sum)
    if node.right:
        self.dfs(node.right, store, pathSum, sum)
    store[pathSum] -= 1
    if store[pathSum] == 0:
        del store[pathSum]

def pathSum(self, root: TreeNode, sum: int) -> int:
    if not root:
        return 0
    
    self.count = 0
    self.dfs(root, {}, 0, sum)
    return self.count



def pathSum(self, root: TreeNode, sum: int) -> int:
    def helper(node, val, lookup):
        
        if(not node): return
        val += node.val
        if(val == sum): self.ans += 1
        if((val-sum) in lookup and lookup[val - sum] > 0):
            self.ans += lookup[val - sum]                     # watchout, lookup[val-sum]
        lookup[val] += 1
        if(node.left): 
            helper(node.left, val, lookup)
        if(node.right): 
            helper(node.right , val, lookup)
        lookup[val] -= 1                                    # if we first move to left side and come back to right side, left side subarray sums shouldn't be there in right side, so backtracking lookup.
        
    self.ans = 0
    helper(root, 0, collections.defaultdict(int) )
    return self.ans



def pathSum(self, root: TreeNode, sum: int) -> int:
    def pathSumSearch(node: TreeNode, cumsum: int) -> int:
        if not node:
            return 0
        
        # add up paths up to <node> and add current cumsum to <prefixes>
        cumsum += node.val
        paths_to_node = prefixes[cumsum - sum]
        prefixes[cumsum] += 1
        
        # going down the tree
        paths_to_children = pathSumSearch(node.left, cumsum) + pathSumSearch(node.right, cumsum)
        
        # going up the tree (remove current cumsum from <prefixes> so non-children won't use it)
        prefixes[cumsum] -= 1
        return paths_to_node + paths_to_children
    
    prefixes = Counter({0: 1})
    return pathSumSearch(root, 0)



def find_paths(self, root, target):
    if root:
        return int(root.val == target) + self.find_paths(root.left, target-root.val) + self.find_paths(root.right, target-root.val)
    return 0

def pathSum(self, root, sum):
    """
    :type root: TreeNode
    :type sum: int
    :rtype: int
    """
    if root:
        return self.find_paths(root, sum) + self.pathSum(root.left, sum) + self.pathSum(root.right, sum)
    return 0


def helper(self, root, target, so_far, cache):
    if root:
        complement = so_far + root.val - target
        if complement in cache:
            self.result += cache[complement]
        cache.setdefault(so_far+root.val, 0)
        cache[so_far+root.val] += 1
        self.helper(root.left, target, so_far+root.val, cache)
        self.helper(root.right, target, so_far+root.val, cache)
        cache[so_far+root.val] -= 1
    return

def pathSum(self, root, sum):
    self.result = 0
    self.helper(root, sum, 0, {0:1})
    return self.result



def pathSum(self, root, target):
    self.ans = 0
    cache = collections.defaultdict(int)
    cache[0] = 1
    
    def dfs(root, cur_sum):
        if not root:
            return 
        cur_sum += root.val
        self.ans += cache[cur_sum - target]
        cache[cur_sum] += 1
        dfs(root.left, cur_sum)
        dfs(root.right, cur_sum)
        cache[cur_sum] -= 1
        
    dfs(root, 0)
    return self.ans



def pathSum(self, root, sum):
    if not root:
        return 0
    self.count=0
    self.helper(root,sum)
    return self.count

def dfs(self,root,sum,count):
    if root.val==sum:
        self.count+=1
    if root.left:
        self.dfs(root.left,sum-root.val,self.count)
    if root.right:
        self.dfs(root.right,sum-root.val,self.count)

def helper(self,root,sum):
    if not root:
        return 
    self.dfs(root,sum,self.count)
    self.helper(root.left,sum)
    self.helper(root.right,sum)



def pathSum(self, root, sum):
    self.res = 0
    self.helper(root,sum)
    return self.res

def dfs(self,root,sum,count,res):
    if not root:
        return
    count += root.val
    if count == sum:
        self.res += 1
    self.dfs(root.left,sum,count,self.res)
    self.dfs(root.right,sum,count,self.res)

def helper(self,root,sum):
    if not root:
        return
    self.dfs(root,sum,0,self.res)
    self.helper(root.left,sum)
    self.helper(root.right,sum)


def pathSum(self, root, s):
        return self.helper(root, s, [s])

    def helper(self, node, origin, targets):
        if not node: return 0
        hit = 0
        for t in targets:
            if not t-node.val: hit += 1                          # count if sum == target
        targets = [t-node.val for t in targets]+[origin]         # update the targets
        return hit+self.helper(node.left, origin, targets)+self.helper(node.right, origin, targets)



def helper(self, node,origin, targets):
    if not node: return 0
    hit=0
    targets+=[origin]
    targets=[i-node.val for i in targets]
    for i in targets:
        if not i: hit+=1
    return hit+self.helper(node.left, origin, targets)+\
    self.helper(node.right, origin, targets)



def dfs(self, root, targets):
    if not root: return 0
    newtargets = [ targets[0] ] + [ target - root.val for target in targets ]
    return targets.count(root.val) + self.dfs(root.left, newtargets) + self.dfs(root.right, newtargets)
       
def pathSum(self, root: TreeNode, k: int) -> int:
    return self.dfs( root, [k] )




def pathSum(self, root, sum):
    def dfs(sumHash, prefixSum, node):
        if not node:
            return 0
		# Sum of current path
        prefixSum += node.val
		# number of paths that ends at current node
        path = sumHash[prefixSum - sum] 
		# add currentSum to prefixSum Hash
        sumHash[prefixSum] += 1
		# traverse left and right of tree
        path += dfs(sumHash, prefixSum, node.left) + dfs(sumHash, prefixSum, node.right)
	    # remove currentSum from prefixSum Hash
        sumHash[prefixSum] -= 1
        return path
    # depth first search, initialize sumHash with prefix sum of 0, occurring once
    return dfs(collections.defaultdict(int, {0: 1}), 0, root)




def pathSum(self, root: TreeNode, sum: int) -> int:
    self.r = 0
    def dfs(root,res):
        if root:
            l = len(res)
            for i in range(l):
                res[i] += root.val
            res.append(root.val)
            for i in res:
                if i == sum:
                    self.r += 1
            left = res[:]
            right = res[:]
            print(res)
            dfs(root.left,left)
            dfs(root.right,right)
    dfs(root,[])
    return self.r



def pathSum(self, root: TreeNode, sum: int) -> int:
        '''如果没有根节点，整个返回值应该为0，没有路径'''
        if not root:
            return 0
        '''
        self.dfs(root, sum)：这个方法是判断以当前点为起点往下是否有path，也就是path的数量，返回值应该是0或1
        self.pathSum(root.left, sum)：对于左节点我依然要考虑以它为起点往下判断
        self.pathSum(root.right, sum)：同上，于是，此时的sum是不变化的，仍然为初始值
        '''
        return self.dfs(root, sum) + self.pathSum(root.left, sum) + self.pathSum(root.right, sum)

























































