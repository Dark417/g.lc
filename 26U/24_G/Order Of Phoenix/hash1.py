
###########################################################################
ez
1. 两数之和
+++

13. 罗马数字转整数
	12. 整数转罗马数字


169. 多数元素
	1150. 检查一个数是否在数组中占绝大多数
	3438. 找到字符串中合法的相邻数字
	2404. 出现最频繁的偶数元素
    !!!

202. 快乐数
!!!



205. 同构字符串

219. 存在重复元素 II
!!!


349. 两个数组的交集

	350. 两个数组的交集 II

	2540. 最小公共值

387. 字符串中的第一个唯一字符


409. 最长回文串


448. 找到所有数组中消失的数字
!!!
+++
    442. 数组中重复的数据

599. 两个列表的最小索引总和


645. 错误的集合



697. 数组的度








###########################################################################
mid

128. 最长连续序列


438. 找到字符串中所有字母异位词


139. 单词拆分

763. 划分字母区间


454. 四数相加 II



36. 有效的数独


740. 删除并获得点数



380. O(1) 时间插入、删除和获取随机元素



491. 非递减子序列
??? backtracking

395. 至少有 K 个重复字符的最长子串



567. 字符串的排列
!!! fixed window
    while
    for


1297. 子串的最大出现次数


2080. 区间内查询数字的频率
???




###########################################################################






13. 罗马数字转整数
def romanToInt(self, s: str) -> int:
    ans = 0
    for x, y in pairwise(s):
        x, y = ROMAN[x], ROMAN[y]
        ans += x if x >= y else -x
    return ans + ROMAN[s[-1]]


def romanToInt(self, s: str) -> int:
        d = {'I':1, 'IV':3, 'V':5, 'IX':8, 'X':10, 'XL':30, 'L':50, 'XC':80, 'C':100, 'CD':300, 'D':500, 'CM':800, 'M':1000}
        return sum(d.get(s[max(i-1, 0):i+1], d[n]) 
        	for i, n in enumerate(s))


    12. 整数转罗马数字
    def intToRoman(self, num: int) -> str:
        hashmap = {1000:'M', 900:'CM', 500:'D', 400:'CD', 100:'C', 90:'XC', 50:'L', 40:'XL', 10:'X', 9:'IX', 5:'V', 4:'IV', 1:'I'}
        res = ''
        for key in hashmap:
        	###
            if num // key != 0:
                count = num // key  # 比如输入4000，count 为 4
                res += hashmap[key] * count 
                num %= key
        return res

        R = (
		    ("", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"),  
		    ("", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"),  
		    ("", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"),  
		    ("", "M", "MM", "MMM"),
		)

		class Solution:
		    def intToRoman(self, num: int) -> str:
		        return R[3][num // 1000] + R[2][num // 100 % 10] + R[1][num // 10 % 10] + R[0][num % 10]



169. 多数元素
def majorityElement(self, nums: List[int]) -> int:
    counts = collections.Counter(nums)
    return max(counts.keys(), key=counts.get)


def majorityElement(self, nums: List[int]) -> int:
    nums.sort()
    return nums[len(nums) // 2]



	1150. 检查一个数是否在数组中占绝大多数
	return nums.count(target) > len(nums) // 2
	count = 0
    for num in nums:
        if num == target:
            count += 1
        elif num > target:
            break
    return count > len(nums) // 2


    3438. 找到字符串中合法的相邻数字
    def findValidPair(self, s: str) -> str:
        cnt = Counter(s)
        for x, y in pairwise(s):
            if x != y and int(x) == cnt[x] and int(y) == cnt[y]:
                return x + y
        return ""


    2404. 出现最频繁的偶数元素
    !!!
    def mostFrequentEven(self, nums: List[int]) -> int:
        cnt = Counter()
        for x in nums:
            if x % 2 == 0:
                cnt[x] += 1
        if len(cnt) == 0: return -1
        mx = max(cnt.values())
        ###
        return min(k for k in cnt if cnt[k] == mx)
        return min(cnt, key=lambda k: (-cnt[k], k))

    def mostFrequentEven(self, nums: List[int]) -> int:
        count = Counter()
        for x in nums:
            if x % 2 == 0:
                count[x] += 1
        res, ct = -1, 0
        for k, v in count.items():
            if res == -1 or v > ct or (v == ct and res > k):
                res = k
                ct = v
        return res

    def mostFrequentEven(self, nums: List[int]) -> int:
        ans = -1
        cnt = Counter()
        for x in nums:
            if x % 2: continue  # 跳过奇数
            cnt[x] += 1
            if cnt[x] > cnt[ans] or cnt[x] == cnt[ans] and x < ans:
                ans = x  # 出现次数最大的数中，值最小的
        return ans




202. 快乐数
!!!



2520. 统计能整除数字的位数
def countDigits(self, num: int) -> int:
    t = num
    res = 0
    while t:
        if num % (t % 10) == 0:
            res += 1
        t //= 10
    return res

##
def countDigits(self, num: int) -> int:
    ans = 0
    x = num
    while x:
        x, d = divmod(x, 10)
        ans += num % d == 0
    return ans


    return sum(1 for c in str(num) if num % int(c) == 0)
    return sum(num % int(c) == 0 for c in str(num) )



205. 同构字符串
!
def isIsomorphic(self, s: str, t: str) -> bool:
    cta = {}
    ctb = {}
    for x, y in zip(s, t):
        if x in cta and cta[x] != y or y in ctb and ctb[y] != x:
            return False
        cta[x] = y


219. 存在重复元素 II
!!! update with bigger index
def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
    dc = {}
    for i, n in enumerate(nums):
        if n in dc and i - dc[n] <= k:
            return True
        dc[n] = i
    return False

def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
    st = set()
    for i, n in enumerate(nums):
        if i > k:
            st.remove(nums[i - k - 1])
        if n in st:
            return True
        st.add(n)
    return False


def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
    st = set()
    for i, x in enumerate(nums):
        if x in st:
            return True
        st.add(x)
        if i >= k:
            st.remove(nums[i - k])
    return False



349. 两个数组的交集
def intersection(self, nums1: List[int], nums2: List[int]) -> List[int]:
    set1 = set(nums1)
    set2 = set(nums2)
    return self.set_intersection(set1, set2)

!!!
def set_intersection(self, set1, set2):
    if len(set1) > len(set2):
        return self.set_intersection(set2, set1)
    return [x for x in set1 if x in set2]


    350. 两个数组的交集 II
    !!
    def intersect(self, nums1: List[int], nums2: List[int]) -> List[int]:
        cnt = Counter(nums1)
        res = []
        for n in nums2:
            if cnt[n] > 0:
                cnt[n] -=1
                res.append(n)
        return res

    2540. 最小公共值
    return min(set(nums1) & set(nums2), default=-1)

    def getCommon(self, nums1: List[int], nums2: List[int]) -> int:
        j = 0
        m = len(nums2)

        for x in nums1:
            while j < m and nums2[j] < x:
                j += 1
            if j < m and nums[j] == x:
                return x
        return -1



387. 字符串中的第一个唯一字符
def firstUniqChar(self, s: str) -> int:
    frequency = collections.Counter(s)
    for i, ch in enumerate(s):
        if frequency[ch] == 1:
            return i
    return -1

###
def firstUniqChar(self, s: str) -> int:
    position = dict()
    n = len(s)
    for i, ch in enumerate(s):
        if ch in position:
            position[ch] = -1
        else:
            position[ch] = i
    first = n
    for pos in position.values():
        if pos != -1 and pos < first:
            first = pos
    if first == n:
        first = -1
    return first

###
def firstUniqChar(self, s: str) -> int:
    position = dict()
    q = collections.deque()
    n = len(s)
    for i, ch in enumerate(s):
        if ch not in position:
            position[ch] = i
            q.append((s[i], i))
        else:
            position[ch] = -1
            while q and position[q[0][0]] == -1:
                q.popleft()
    return -1 if not q else q[0][1]


409. 最长回文串
def longestPalindrome(self, s: str) -> int:
    res = odd = 0
    ct = Counter(s)
    for v in ct.values():
        rem = v % 2
        res += v - rem
        if rem == 1:
            odd = 1
    return res + odd



448. 找到所有数组中消失的数字
#mod
def findDisappearedNumbers(self, nums: List[int]) -> List[int]:
    n = len(nums)
    for nm in nums:
        nums[(nm - 1) % n] += n
    return [i + 1 for i, x in enumerate(nums) if x <= n]


    442. 数组中重复的数据
    !!!



599. 两个列表的最小索引总和
def findRestaurant(self, list1: List[str], list2: List[str]) -> List[str]:
    st1 = {}
    for i, st in enumerate(list1):
        if st not in st1:
            st1[st] = i
    shared = {}
    for i, st in enumerate(list2):
        if st in st1 and st not in shared:
            shared[st] = st1[st] + i
    return [k for k in shared.keys() if shared[k] == min(shared.values())]


645. 错误的集合
# public int[] findErrorNums(int[] nums) {
#     int[] errorNums = new int[2];
#     int n = nums.length;
#     Arrays.sort(nums);
#     int prev = 0;
#     for (int i = 0; i < n; i++) {
#         int curr = nums[i];
#         if (curr == prev) {
#             errorNums[0] = prev;
#         } else if (curr - prev > 1) {
#             errorNums[1] = prev + 1;
#         }
#         prev = curr;
#     }
#     if (nums[n - 1] != n) {
#         errorNums[1] = n;
#     }
#     return errorNums;
# }

# public int[] findErrorNums(int[] nums) {
#     int[] errorNums = new int[2];
#     int n = nums.length;
#     Map<Integer, Integer> map = new HashMap<Integer, Integer>();
#     for (int num : nums) {
#         map.put(num, map.getOrDefault(num, 0) + 1);
#     }
#     for (int i = 1; i <= n; i++) {
#         int count = map.getOrDefault(i, 0);
#         if (count == 2) {
#             errorNums[0] = i;
#         } else if (count == 0) {
#             errorNums[1] = i;
#         }
#     }
#     return errorNums;
# }


697. 数组的度
def findShortestSubArray(self, nums: List[int]) -> int:
    cnt = {}
    for i, n in enumerate(nums):
        if n not in cnt:
            cnt[n] = [i]
        else:
            cnt[n].append(i)
    degree = max(len(v) for v in cnt.values())
    min_length = len(nums)
    for k, v in cnt.items():
        if len(v) == degree:
            min_length = min(min_length, v[-1] - v[0] + 1)
    return min_length




734. 句子相似性
def areSentencesSimilar(self, sentence1: List[str], sentence2: List[str], similarPairs: List[List[str]]) -> bool:
        if len(sentence1) != len(sentence2): 
            return False
        pairset = set(map(tuple, similarPairs))
        return all(w1 == w2 or (w1, w2) in pairset or (w2, w1) in pairset
                   for w1, w2 in zip(sentence1, sentence2))





819. 最常见的单词
def mostCommonWord(self, paragraph: str, banned: List[str]) -> str:
    sts = paragraph.split(" ,")
    ban = set(banned)
    freq = Counter()
    word = ""
    n = len(paragraph)
    for i in range(n + 1):
        if i < n and paragraph[i].isalpha():
            word += paragraph[i].lower()
        elif word:
            if word not in ban:
                freq[word] += 1
            word = ""
    maxF = max(freq.values())
    return next(word for word, f in freq.items() if f == maxF)

    return max(freq, key=freq.get)




###########################################################################
mid

128. 最长连续序列
def longestConsecutive(self, nums: List[int]) -> int:
    longest = 0
    st = set(nums)

    for num in st:
        if num - 1 not in st:
            cur_num = num
            cur_longest = 1

            while cur_num + 1 in st:
                cur_num = cur_num + 1
                cur_longest += 1

            longest = max(longest, cur_longest)
    return longest



def longestConsecutive(self, nums: List[int]) -> int:
    ans = 0
    st = set(nums)  
    for x in st:
        if x - 1 in st:
            continue
        y = x + 1
        while y in st:
            y += 1
        ans = max(ans, y - x)
    return ans





438. 找到字符串中所有字母异位词
def findAnagrams(self, s: str, p: str) -> List[int]:
    l = len(p)
    pcnt = Counter(p)
    res = []
    scnt = Counter(s[:l])
    if scnt == pcnt:
        res.append(0)

    for i in range(len(s) - l):
        scnt[s[i]] -= 1
        scnt[s[i + l]] += 1
        
        if scnt == pcnt:
            res.append(i + 1)
    return res


139. 单词拆分
def wordBreak(self, s: str, wordDict: List[str]) -> bool:
    maxleng = max(map(len, wordDict))
    ss = set(wordDict)

    @cache
    def dfs(i):
        if i == 0:
            return True
        for j in range(i - 1, max(-1, i - maxleng - 1), -1):
            if s[j: i] in ss and dfs(j):
                return True
        return False

    return dfs(len(s))




763. 划分字母区间
def partitionLabels(self, s: str) -> List[int]:
    last = [0] * 26
    for i in range(len(s)):
        last[s[i]] = i
    start = end = 0
    res = []
    for i in range(len(s)):
        end = max(end, last[s[i]])
        if i == end:
            res.append(end - start + 1)
            start = end + 1
    return res



454. 四数相加 II
def fourSumCount(self, nums1: List[int], nums2: List[int], nums3: List[int], nums4: List[int]) -> int:
    cnt = Counter(x + y for x in nums1 for y in nums2)
    return sum(cnt[-x - y] for x in nums3 for y in nums4)





36. 有效的数独
def isValidSudoku(self, board: List[List[str]]) -> bool:
    row = [[0] * 9 for _ in range(9)]
    col = [[0] * 9 for _ in range(9)]
    block = [[0] * 9 for _ in range(9)]
    for i in range(9):
        for j in range(9):
            if board[i][j] != ".":
                num = int(board[i][j]) - 1
                b = i//3 * 3 + j//3
                if row[i][num] or col[j][num] or block[b][num]:
                    return False
                row[i][num] = col[j][num] = block[b][num] = 1
    return True





740. 删除并获得点数
def deleteAndEarn(self, nums: List[int]) -> int:
    store = [0] * (max(nums) + 1)
    for x in nums:
        store[x] += x
    f0 = f1 = 0
    for x in store:
        f0, f1 = f1, max(f1, f0 + x)
    return f1

def deleteAndEarn(self, nums: List[int]) -> int:
    store = [0] * (max(nums) )
    for x in nums:
        store[x-1] += x
    f0 = f1 = 0
    for x in store:
        f0, f1 = f1, max(f1, f0 + x)
    return f1



380. O(1) 时间插入、删除和获取随机元素
class RandomizedSet:

    def __init__(self):
        self.nums = []
        self.dc = {}

    def insert(self, val: int) -> bool:
        if val in self.dc:
            return False
        self.dc[val] = len(self.nums)
        self.nums.append(val)

    ###
    def remove(self, val: int) -> bool:
        if val not in self.dc:
            return False
        idx = self.dc[val]
        self.nums[idx] = self.nums[-1]
        self.dc[self.nums[idx]] = idx
        self.nums.pop()
        del self.dc[val]
        return True

    def getRandom(self) -> int:
        return choice(self.nums)



491. 非递减子序列






395. 至少有 K 个重复字符的最长子串
def longestSubstring(self, s: str, k: int) -> int:
    if len(s) < k:
        return 0
    for c in set(s):
        if s.count(c) < k:
            return max(self.longestSubstring(t, k) for t in s.split(c))
    return len(s)


# public int longestSubstring(String s, int k) {
#     int n = s.length();
#     return dfs(s, 0, n - 1, k);
# }

# public int dfs(String s, int l, int r, int k) {
#     int[] cnt = new int[26];
#     for (int i = l; i <= r; i++) {
#         cnt[s.charAt(i) - 'a']++;
#     }

#     char split = 0;
#     for (int i = 0; i < 26; i++) {
#         if (cnt[i] > 0 && cnt[i] < k) {
#             split = (char) (i + 'a');
#             break;
#         }
#     }
#     if (split == 0) {
#         return r - l + 1;
#     }

#     int i = l;
#     int ret = 0;
#     while (i <= r) {
#         while (i <= r && s.charAt(i) == split) {
#             i++;
#         }
#         if (i > r) {
#             break;
#         }
#         int start = i;
#         while (i <= r && s.charAt(i) != split) {
#             i++;
#         }

#         int length = dfs(s, start, i - 1, k);
#         ret = Math.max(ret, length);
#     }
#     return ret;
# }


567. 字符串的排列
def checkInclusion(self, s1: str, s2: str) -> bool:
    cnt1 = Counter(s1)
    len1 = len(s1)
    len2 = len(s2)
    for i in range(len2 - len1 + 1):
        if Counter(s2[i: i+ len1]) == cnt1:
            return True
    return False

def checkInclusion(self, s1: str, s2: str) -> bool:
    if len(s1) > len(s2):
        return False
    cnt1 = Counter(s1)
    cntc = Counter(s2[:len(s1)])

    if cntc == cnt1:
        return True

    for i in range(len(s1), len(s2)):
        cntc[s2[i - len(s1)]] -= 1
        if cntc[s2[i]] == 0:
            del cntc[s2[i]]

        cntc[s2[i]] += 1
        if cnt1 == cntc:
            return True
    return False


def checkInclusion(self, s1, s2):
    counter1 = collections.Counter(s1)
    N = len(s2)
    left = 0
    right = len(s1) - 1
    counter2 = collections.Counter(s2[0:right])

    while right < N:
        counter2[s2[right]] += 1
        if counter1 == counter2:
            return True
        counter2[s2[left]] -= 1
        if counter2[s2[left]] == 0:
            del counter2[s2[left]]
        left += 1
        right += 1
    return False


def checkInclusion(self, s1: str, s2: str) -> bool:
    if len(s1) > len(s2):
        return False
    
    cnt1 = Counter(s1)
    len1 = len(s1)
    cnt2 = Counter(s2[:len1])
    
    if cnt2 == cnt1:
        return True

    i = len1  
    while i < len(s2):
        left_char = s2[i - len1]
        cnt2[left_char] -= 1
        if cnt2[left_char] == 0:
            del cnt2[left_char]
        
        right_char = s2[i]
        cnt2[right_char] += 1
        
        if cnt2 == cnt1:
            return True
    
        i += 1
    return False



442. 数组中重复的数据
def findDuplicates(self, nums: List[int]) -> List[int]:
    ans = []
    for x in nums:
        x = abs(x)
        if nums[x - 1] > 0:
            nums[x - 1] = -nums[x - 1]
        else:
            ans.append(x)
    return ans



def findDuplicates(self, nums: List[int]) -> List[int]:
    for i in range(len(nums)):
        while nums[i] != nums[nums[i] - 1]:
            nums[nums[i] - 1], nums[i] = nums[i], nums[nums[i] - 1]
    return [num for i, num in enumerate(nums) if num - 1 != i]



1297. 子串的最大出现次数



2080. 区间内查询数字的频率


2537. 统计好子数组的数目

























































































































































































































