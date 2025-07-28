# 47. 全排列 II

return list(map(list, set(itertools.permutations(nums))))



def permuteUnique(nums):
    res = []
    nums.sort()
    dfs(nums, [], res)
    return res
    
def dfs(nums, path, res):
    if not nums:
        res.append(path)
    else:
        for i in range(len(nums)):
            if i > 0 and nums[i] == nums[i-1]:
                continue
            dfs(nums[:i]+nums[i+1:], path+[nums[i]], res)



def permuteUnique(self, nums: List[int]) -> List[List[int]]:
    if len(nums) == 1:
        return [nums]
    res = []
    visit = set()
    for i in range(len(nums)):
        if nums[i] not in visit:
            visit.add(nums[i])
            pre = [nums[i]]
            permutations = self.permuteUnique(nums[:i]+nums[i+1:])
            for p in permutations:
                res.append(pre+p)
    return res

        
def permuteUnique(self, nums):
    return reduce(lambda a,n:[l[:i]+[n]+l[i:]for l in a for i in xrange((l+[n]).index(n)+1)],nums,[[]])

    ans = [[]]
    for n in nums:
        ans = [l[:i]+[n]+l[i:]
               for l in ans
               for i in range((l+[n]).index(n)+1)]
    return ans



def permuteUnique(self, nums):
    ans = [[]]
    for n in nums:
        new_ans = []
        for l in ans:
            for i in range(len(l)+1):
                new_ans.append(l[:i]+[n]+l[i:])
                if i<len(l) and l[i]==n: break              #handles duplication
        ans = new_ans
    return ans



def permuteUnique(self, nums):
    res = []
    nums.sort()
    self.dfs(nums, [], res)
    return res
    


def permuteUnique(self, nums: List[int]) -> List[List[int]]:
    nums.sort()
    self.res = []
    check = [0 for i in range(len(nums))]
    
    self.backtrack([], nums, check)
    return self.res
    
def backtrack(self, sol, nums, check):
    if len(sol) == len(nums):
        self.res.append(sol)
        return
    
    for i in range(len(nums)):
        if check[i] == 1:
            continue
        if i > 0 and nums[i] == nums[i-1] and check[i-1] == 0:
            continue
        check[i] = 1
        self.backtrack(sol+[nums[i]], nums, check)
        check[i] = 0



def permuteUnique(self, nums: List[int]) -> List[List[int]]:
    def dfs(nums, size, depth, path, used, res):
        if depth == size:
            res.append(path.copy())
            return
        for i in range(size):
            if not used[i]:

                if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                    continue

                used[i] = True
                path.append(nums[i])
                dfs(nums, size, depth + 1, path, used, res)
                used[i] = False
                path.pop()

    size = len(nums)
    if size == 0:
        return []

    nums.sort()

    used = [False] * len(nums)
    res = []
    dfs(nums, size, 0, [], used, res)
    return res




"""
public List<List<Integer>> permuteUnique(int[] nums) {
        List<List<Integer>> ans = new ArrayList<List<Integer>>();
        List<Integer> perm = new ArrayList<Integer>();
        vis = new boolean[nums.length];
        Arrays.sort(nums);
        backtrack(nums, ans, 0, perm);
        return ans;
    }

    public void backtrack(int[] nums, List<List<Integer>> ans, int idx, List<Integer> perm) {
        if (idx == nums.length) {
            ans.add(new ArrayList<Integer>(perm));
            return;
        }
        for (int i = 0; i < nums.length; ++i) {
            if (vis[i] || (i > 0 && nums[i] == nums[i - 1] && !vis[i - 1])) {
                continue;
            }
            perm.add(nums[i]);
            vis[i] = true;
            backtrack(nums, ans, idx + 1, perm);
            vis[i] = false;
            perm.remove(idx);
        }
    }





"""





















