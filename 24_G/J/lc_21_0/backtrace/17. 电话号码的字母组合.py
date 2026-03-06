"""
095.17. Letter Combinations of a Phone Number
电话号码的字母组合


Given a string containing digits from 2-9 inclusive, return all possible letter 
ombinations that the number could represent.

A mapping of digit to letters (just like on the telephone buttons) is given 
below. Note that 1 does not map to any letters.



Example:

Input: "23"
Output: ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"].
Note:

Although the above answer is in lexicographical order, your answer could be in 
any order you want.



"""

# https://leetcode.com/problems/letter-combinations-of-a-phone-number/discuss/8362/3-different-method-for-this-question.(recursive-dfs-bfs-iterative-dfs)


"""

/* DFS recursive */
public void search(List<String> list, String str, int i, String digits, char[][] dict) {
	if (i == digits.length()) {
		list.add(str);
		return;
	}
	char[] candidates = dict[digits.charAt(i) - '2'];
	for (char c : candidates)
		search(list, str + "" + c, i + 1, digits, dict);
}


/* BFS */
public List<String> searchFIFO(String digits, char[][] dict) {
	Queue<String> queue = new LinkedList<String>();
	for (char c : dict[digits.charAt(0) - '2']) {
		queue.add("" + c);
	}
	for (int step = 1; step < digits.length(); step++) {
		int size = queue.size();
		while (size-- > 0) {
			String lastLayerString = queue.poll();
			for (char c : dict[digits.charAt(step) - '2']) {
				queue.add(lastLayerString + "" + c);
			}
		}
	}
	// System.out.println(queue);
	return new ArrayList<String>(queue);
}



/* DFS iterative */
public List<String> search(String digits, char[][] dict) {
	List<String> list = new ArrayList<String>();
	int[] stack = new int[digits.length()];
	int step = 0;
	char[] result = new char[digits.length()];
	// the limit number of choices in step 0
	int limit0 = dict[digits.charAt(0) - '2'].length;
	while (stack[0] < limit0) {
		if (stack[step] == dict[digits.charAt(step) - '2'].length) {
			// if No.step has reach its limit, then backtrack
			stack[step] = 0;
			// trace back to last step, and prepare to search the next
			// choice
			stack[--step]++;
			continue;
		}
		if (step == digits.length() - 1) {
			// this search branch is end
			for (int i = 0; i <= step; i++) {
				result[i] = dict[digits.charAt(i) - '2'][stack[i]];
			}
			list.add(new String(result));
			stack[step]++;
		} else {
			step++;
		}
	}
	return list;
}


"""
def letterCombinations(self, digits: str) -> List[str]:
    dc = {"1":"!@#", "2":"abc", "3":"def", "4":"ghi", "5":"jkl", "6":"mno", "7":"pqrs", "8":"tuv","9":"wxyz",}
    res = []
    for d in digits:
        if res == []:
            res = [i for i in dc[d]]
        else:
            res = [ x+i for x in res for i in dc[d]]
    return res





def letterCombinations(self, digits: str) -> List[str]:
    if not digits:
        return list()
    
    phoneMap = {
        "2": "abc",
        "3": "def",
        "4": "ghi",
        "5": "jkl",
        "6": "mno",
        "7": "pqrs",
        "8": "tuv",
        "9": "wxyz",
    }

    def backtrack(index: int):
        if index == len(digits):
            combinations.append("".join(combination))
        else:
            digit = digits[index]
            for letter in phoneMap[digit]:
                combination.append(letter)
                backtrack(index + 1)
                combination.pop()

    combination = list()
    combinations = list()
    backtrack(0)
    return combinations



def letterCombinations(self, digits: str) -> List[str]:
    if not digits: return []

    phone = {'2':['a','b','c'],
             '3':['d','e','f'],
             '4':['g','h','i'],
             '5':['j','k','l'],
             '6':['m','n','o'],
             '7':['p','q','r','s'],
             '8':['t','u','v'],
             '9':['w','x','y','z']}
            
    def backtrack(conbination,nextdigit):
        if len(nextdigit) == 0:
            res.append(conbination)
        else:
            for letter in phone[nextdigit[0]]:
                backtrack(conbination + letter,nextdigit[1:])

    res = []
    backtrack('',digits)
    return res




def letterCombinations(self, digits: str) -> List[str]:
        if not digits: return []
        phone = ['abc','def','ghi','jkl','mno','pqrs','tuv','wxyz']
        queue = ['']  # 初始化队列
        for digit in digits:
            for _ in range(len(queue)):
                tmp = queue.pop(0)
                for letter in phone[ord(digit)-50]:# 这里我们不使用 int() 转换字符串，使用ASCII码
                    queue.append(tmp + letter)
        return queue


def letterCombinations(self, digits):
    if not digits:
        return []
    d = [" ","*","abc","def","ghi","jkl","mno","pqrs","tuv","wxyz"]
    res = []
    
    def dfs(tmp,index):
        if index==len(digits):
            res.append(tmp)
            return
        c = digits[index]
        letters = d[ord(c)-48]
        
        for i in letters:
            dfs(tmp+i,index+1)
    dfs("",0)
    return res




import collections
class Solution:
    def letterCombinations(self, digits: str) -> List[str]:
        mapping = ['', '', 'abc', 'def', 'ghi', 'jkl', 'mno', 'pqrs', 'tuv', 'wxyz']
        result = collections.deque([''])
        for d in digits:
            for _ in range(len(result)):
                prev = result.popleft()
                for letter in mapping[int(d)]:
                    result.append(prev + letter)
        return result if digits else ''


import itertools
class Solution:
    def letterCombinations(self, digits: str) -> List[str]:
        mapping = {'2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl', '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'}
        return list(map(''.join, itertools.product(*map(mapping.__getitem__, digits)))) if digits else ''






def letterCombinations(self, digits: str) -> List[str]:
    if not digits: return []
    digit_map = {'2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl', '6': 'mno', 
                 '7': 'pqrs', '8': 'tuv', '9': 'wxyz'}
    result = ['']
    for idx in range(len(digits)):
        result = [prev + l for prev in result for l in digit_map[digits[idx]]]
    return result




def letterCombinations(self, digits):
    if '' == digits: return []
    kvmaps = {
        '2': 'abc',
        '3': 'def',
        '4': 'ghi',
        '5': 'jkl',
        '6': 'mno',
        '7': 'pqrs',
        '8': 'tuv',
        '9': 'wxyz'
    }
    return reduce(lambda acc, digit: [x + y for x in acc for y in kvmaps[digit]], digits, [''])


def letterCombinations(self, digits):
    b = {"2":"abc", "3":"def", "4":"ghi", "5":"jkl", "6":"mno", "7":"pqrs", "8":"tuv", "9":"wxyz"}
    return [] if digits == "" else [ "".join(x) for x in itertools.product(*(b[d] for d in digits if d in b))]


def letterCombinations(self, digits):
    map = {'2':'abc', '3':'def', '4':'ghi', '5':'jkl', '6':'mno', '7':'pqrs', '8':'tuv', '9':'wxyz'}
    if len(digits) == 0: return []
    return [a+b for a in self.letterCombinations(digits[:-1])
                for b in self.letterCombinations(digits[-1] )] or list(map[digits])




def letterCombinations(self, digits):
    phone = {
        '2': 'abc',
        '3': 'def',
        '4': 'ghi',
        '5': 'jkl',
        '6': 'mno',
        '7': 'pqrs',
        '8': 'tuv',
        '9': 'wxyz'
    }
    if(len(digits) == 0):
        return []
    answer = [""]
    for digit in digits:
        outside_answer = answer[:]
        for letter in phone[digit]:
            for ans in outside_answer:
                answer.append(ans + letter)
    
    return [x for x in answer if len(x) == len(digits)]


	combs = [""]
    for digit in digits:
        new_combs = []
        for comb in combs:
            for letter in nums_to_letters[int(digit)]:
                new_combs.append(comb + letter)
        combs = new_combs
        
    return combs


	all_combinations = [''] if digits else []
    for digit in digits:
        current_combinations = list()
        for letter in interpret_digit[digit]:
            for combination in all_combinations:
                current_combinations.append(combination + letter)
        all_combinations = current_combinations
        return all_combinations



def letterCombinations(self, digits):
    dict = {'2':"abc", '3':"def", '4':"ghi", '5':"jkl", '6':"mno", '7': "pqrs", 
        '8':"tuv", '9':"wxyz"}
    cmb = [''] if digits else []
    for d in digits:
        cmb = [p + q for p in cmb for q in dict[d]]
    return cmb


def letterCombinations(self, digits):
	MAPPING = ('0', '1', 'abc', 'def', 'ghi', 'jkl', 'mno', 'pqrs', 'tuv', 'wxyz')

	res = ['']
	for d in digits:
	    [pre + cur for pre in res for cur in MAPPING[int(d)]
	return res if len(digits) > 0 else []


def letterCombinations(self, digits):
    map_ = {
        '2' : 'abc',
        '3' : 'def',
        '4' : 'ghi',
        '5' : 'jkl',
        '6' : 'mno',
        '7' : 'pqrs',
        '8' : 'tuv',
        '9' : 'wxyz'
    }
    result = []
    
    def make_combinations(i, cur):
        if i == len(digits):
            if len(cur) > 0:
                result.append(''.join(cur))
            return
        for ch in map_[digits[i]]:
            cur.append(ch)
            make_combinations(i+1, cur)
            cur.pop()
    
    make_combinations(0, [])
    
    return result





def letterCombinations(self, digits: str) -> List[str]:
    if not digits:
        return []
    cache = {"2":"abc","3":"def","4":"ghi","5":"jkl","6":"mno","7":"pqrs","8":"tuv","9":"wxyz"}        
    return self.backtrack(digits,[[]],cache)    

def backtrack(self,rem,result,cache):
    if not rem:
        return result     
    if len(rem) == 1:            
        return list(cache[rem])
    output = []
    result = self.backtrack(rem[1:],result,cache)
    for d in cache[rem[0]]:                                      
        for r in result:
            output.append(d+str(r))                
    return output


seldata = bmiData[which(bmiData$height_in>60)]

#x = subset(bmiData, "height_in" > 60)
#bmiData[which(bmiData$"height_in">60)]



#x = bmiData[ which(bmiData$"height_in" > 65)]
#print(x)

#library(dplyr)
#data = bmiData %>% select(name:"height_in")


#data <- bmiData[which(bmiData["height_in"]> 60),]
#print(data)
#seldata <- subset(bmiData, "height_in" > 60)
#seldata <- subset(airquality, "height_in" > 60, select = "height_in")
#seldata <- which(bmiData$height_in > 62)



def letterCombinations(self, digits):
    numletter = {
                '2': 'abc',
                '3': 'def',
                '4': 'ghi',
                '5': 'jkl',
                '6': 'mno',
                '7': 'pqrs',
                '8': 'tuv',
                '9': 'wxyz'
            }
    
    letters = [numletter[i] for i in digits]
    from functools import reduce
    if digits:
        if len(digits) == 1:
            return list(numletter[digits])
        else:
            return reduce((lambda x, y: [i + j for i in x for j in y]), letters) 
    else:
        return []


# map
def letterCombinations(self, digits):
    if not digits:
        return []
    mapping = {'0':'', '1':'', '2':'abc', '3':'def', '4':'ghi', '5':'jkl', '6':'mno', '7':'pqrs', '8':'tuv', '9':'wxyz'}
    groups = [mapping[d] for d in digits if d != '0' and d != '1']
    return [''.join(x) for x in itertools.product(*groups)]



def letterCombinations(self, digits):
    dic = {
        '1':'*', '2':'abc', '3':'def',
        '4':'ghi', '5':'jkl', '6':'mno',
        '7':'qprs', '8':'tuv', '9':'wxyz',
        '0':' '
    }
    
    def generate(segment, digits, letter=[]):
        if not digits:
            letter.append(segment)
            return []
        for i in dic[digits[0]]:
            generate(segment+i, digits[1:])
        return letter
    return generate('',digits)




# caikehe
def letterCombinations(self, digits):
    if not digits:
        return []
    dic = {"2":"abc", "3":"def", "4":"ghi", "5":"jkl", "6":"mno", "7":"pqrs", "8":"tuv", "9":"wxyz"}
    res = []
    self.dfs(digits, dic, 0, "", res)
    return res
    
def dfs(self, digits, dic, index, path, res):
    if len(path) == len(digits):
        res.append(path)
        return 
    for i in xrange(index, len(digits)):
        for j in dic[digits[i]]:
            self.dfs(digits, dic, i+1, path+j, res)







def letterCombinations(self, digits):
    if not digits:
        return []
    
    digit_string_map = {'2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno','7':'pqrs','8':'tuv','9':'wxyz'}
    
    res = [""]
    for digit in digits:
        new_res = []
        for ch in digit_string_map[digit]:
            new_res.extend([ele+ch for ele in res])
        res = new_res
    return res


	if not digits: return []
    digit_map = {'2':'abc','3':'def','4':'ghi','5':'jkl',
                '6':'mno','7':'pqrs','8':'tuv','9':'wxyz'}
    # start with no built up combos
    combos = ['']
    # for each digit in the main string
    for d in digits:
        # for each letter in the digit map of this digit,
        # add to combos that letter appended to all
        # built up combos of the letters before it
        combos = [c + l for l in digit_map[d] for c in combos]
    return combos



def letterCombinations(self, digits):
    if not digits:
        return []
    dict = {"1":None,"2":["a","b","c"],"3":["d","e","f"],"4":["g","h","i"],
            "5":["j","k","l"],"6":["m","n","o"],"7":["p","q","r","s"],
            "8":["t","u","v"],"9":["w","x","y","z"]}
            
    def dfs(dict,string,index,path,res):
        if index ==len(string):
            res.append(path)
            return
        for i in dict[string[index]]:
            dfs(dict,string,index+1,path+i,res)
    res = []        
    dfs(dict,digits,0,"",res)
    return res









def letterCombinations(self, digits: str) -> List[str]:
	phone = {
		'2': ['a', 'b', 'c'],
             '3': ['d', 'e', 'f'],
             '4': ['g', 'h', 'i'],
             '5': ['j', 'k', 'l'],
             '6': ['m', 'n', 'o'],
             '7': ['p', 'q', 'r', 's'],
             '8': ['t', 'u', 'v'],
             '9': ['w', 'x', 'y', 'z']
	} 

	n = len(digits)
	res = []
	def backtrack(cur, left):
		if len(cur) == n:
			res.append(cur)
		else:
			for l in phone[left[0]]:
				backtrack(cur+l, left[1:])

	if digits:
		backtrack("", digits)
	return res





# official
def letterCombinations(self, digits):
    phone = {'2': ['a', 'b', 'c'],
             '3': ['d', 'e', 'f'],
             '4': ['g', 'h', 'i'],
             '5': ['j', 'k', 'l'],
             '6': ['m', 'n', 'o'],
             '7': ['p', 'q', 'r', 's'],
             '8': ['t', 'u', 'v'],
             '9': ['w', 'x', 'y', 'z']}
            
    def backtrack(combination, next_digits):
        # if there is no more digits to check
        if len(next_digits) == 0:
            # the combination is done
            output.append(combination)
        # if there are still digits to check
        else:
            # iterate over all letters which map 
            # the next available digit
            for letter in phone[next_digits[0]]:
                # append the current letter to the combination
                # and proceed to the next digits
                backtrack(combination + letter, next_digits[1:])
                
    output = []
    if digits:
        backtrack("", digits)
    return output


# by index
def letterCombinations(self, digits):
	# 注意边界条件
	if not digits:
		return []
	# 一个映射表，第二个位置是"abc“,第三个位置是"def"。。。
	# 这里也可以用map，用数组可以更节省点内存
	d = [" ","*","abc","def","ghi","jkl","mno","pqrs","tuv","wxyz"]
	# 最终输出结果的list
	res = []
	
	# 递归函数
	def dfs(tmp,index):
		# 递归的终止条件，注意这里的终止条件看上去跟动态演示图有些不同，主要是做了点优化
		# 动态图中是每次截取字符串的一部分，"234"，变成"23"，再变成"3"，最后变成""，这样性能不佳
		# 而用index记录每次遍历到字符串的位置，这样性能更好
		if index==len(digits):
			res.append(tmp)
			return
		# 获取index位置的字符，假设输入的字符是"234"
		# 第一次递归时index为0所以c=2，第二次index为1所以c=3，第三次c=4
		# subString每次都会生成新的字符串，而index则是取当前的一个字符，所以效率更高一点
		c = digits[index]
		# map_string的下表是从0开始一直到9， ord(c)-48 是获取c的ASCII码然后-48,48是0的ASCII
		# 比如c=2时候，2-'0'，获取下标为2,letter_map[2]就是"abc"
		letters = d[ord(c)-48]
		
		# 遍历字符串，比如第一次得到的是2，页就是遍历"abc"
		for i in letters:
			# 调用下一层递归，用文字很难描述，请配合动态图理解
			dfs(tmp+i,index+1)
	dfs("",0)
	return res


















































































































