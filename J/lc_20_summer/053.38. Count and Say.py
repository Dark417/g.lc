"""
053.38. Count and Say
外观数列

The count-and-say sequence is the sequence of integers with the first five terms as following:

1.     1
2.     11
3.     21
4.     1211
5.     111221

1 is read off as "one 1" or 11.
11 is read off as "two 1s" or 21.
21 is read off as "one 2, then one 1" or 1211.

Given an integer n where 1 ≤ n ≤ 30, generate the nth term of the count-and-say 
sequence. You can do so recursively, in other words from the previous member read 
off the digits, counting the number of digits in groups of the same digit.

Note: Each term of the sequence of integers will be represented as a string.

 

Example 1:

Input: 1
Output: "1"
Explanation: This is the base case.
Example 2:

Input: 4
Output: "1211"
Explanation: For n = 3 the term was "21" in which we have two groups "2" and
"1", "2" can be read as "12" which means frequency = 1 and value = 2, 
the same way "1" is read as "11", so the answer is the concatenation of "12" and "11" which is "1211".



"""

def countAndSay(self, n):
    s = '1'
    for _ in range(n - 1):
        s = re.sub(r'(.)\1*', lambda m: str(len(m.group(0))) + m.group(1), s)
    return s

def countAndSay(self, n):
    s = '1'
    for _ in range(n - 1):
        s = ''.join(str(len(group)) + digit
                    for group, digit in re.findall(r'((.)\2*)', s))
    return s

def countAndSay(self, n):
    s = '1'
    for _ in range(n - 1):
        s = ''.join(str(len(list(group))) + digit
                    for digit, group in itertools.groupby(s))
    return s


# recursion
def countAndSay(self, n: int) -> str:
    if n <= 1:
        return '1'
    pre = self.countAndSay(n - 1)

    res = ''
    count = 1
    for idx in range(len(pre)):

        if idx == 0 :
            count = 1

        elif pre[idx] != pre[idx -1]:
            tmp = str(count) + pre[idx-1]
            res += tmp
            count = 1
        elif pre[idx] == pre[idx-1]:
            count +=1

        if idx == len(pre) - 1:
            tmp = str(count) + pre[idx]
            res += tmp
    return res


def countAndSay(self, n: int) -> str:
    if n==1:
        return "1"
    return self.bs(self.countAndSay(n-1))
    
    def bs(self, string):
        lis=list(string)
        lis.append('0') #末尾补一个，方便后续计数
        lis1=[]
        re=0
        i=0
        while i<len(lis)-1:
            if lis[i]!=lis[i+1]:
                lis1.append(str(i+1-re)) #当前计录的值的个数
                lis1.append(lis[i]) #当前记录的值
                re=i+1         
            i=i+1
        s=''.join(lis1) #列表转字符串
        return s


def countAndSay(self, n: int) -> str:
        if(n == 1): return '1'
        num = self.countAndSay(n-1)+"*"
        print(num)
        temp = list(num)
        count = 1
        strBulider = ''
        # print(len(temp))
        for i in range(len(temp)-1):
            if  temp[i] == temp[i+1] :
                    count += 1  
            else:
                if temp[i] != temp[i+1]:
                    strBulider +=  str(count) + temp[i]
                    count = 1
        return strBulider





def countAndSay(self, n):
    s = '1'
    for _ in range(n-1):
        let, temp, count = s[0], '', 0
        for l in s:
            if let == l:
                count += 1
            else:
                temp += str(count)+let
                let = l
                count = 1
        temp += str(count)+let
        s = temp
    return s


def countAndSay(self, n):
    result = '1'
    for _ in range(n-1):
        prev = result
        result = ''
        j = 0
        while j < len(prev):
            cur = prev[j]
            cnt = 1
            j += 1
            while j < len(prev) and prev[j] == cur:
                cnt += 1
                j += 1
            result += str(cnt) + str(cur)
    return result


def countAndSay(self, n):
    if n == 1: return "1"
    s = self.countAndSay(n-1)
    i, ch, tmp = 0, s[0], ''
    for j in range(1, len(s)):
        if s[j] != ch:
            tmp += str(j-i) + ch
            i, ch = j, s[j]
    tmp += str(len(s)-i) + ch
    return tmp


def countAndSay(self, n: int) -> str:
        output = '1'
        for i in range(n-1):
            output = ''.join([str(len(list(g))) + k for k, g in groupby(output)])
        return output


def countAndSay(n):
    result = "1"
    for _ in range(n - 1):
        # original
        # s = ''.join(str(len(list(group))) + digit for digit, group in itertools.groupby(s))
        
        # decomposed
        v = '' # accumulator string
        # iterate the characters (digits) grouped by digit
        for digit, group in itertools.groupby(result):
            count = len(list(group)) # eg. the 2 in two 1s 
            v += "%i%s" % (count, digit) # create the 21 string and accumulate it
        result = v # save to result for the next for loop pass

    # return the accumulated string
    return result


def countAndSay(self, n):
    if n == 1:
        return str(1)
    if n == 2:
        return '11'
    num = 1
    res = []
    while num < n-1:
        a = [0 for i in range(10)]
        if num == 1:
            L = [1, 1]
        else:
            L = res
            res = []
        for ind, i in enumerate(L):
            if ind == 0:
                a[i] += 1
            else:
                a[i] += 1
                pre = L[ind-1]
                if i != pre:
                    res.append(a[pre])
                    res.append(pre)
                    a[pre] = 0
        res.append(a[i])
        res.append(i)
        num += 1
    res = ''.join([str(i) for i in res])
    return res


def countAndSay(self, n: int) -> str:
    num = []
    num.append("")
    num.append("1")
    if n==1: return num[1]
    for i in range(2,n+1):
        p = []
        s = ""
        for x in num[i-1]:
            if p==[] or x==p[0]:
                p.append(x)
            else:
                s += str(len(p))
                s += p[0]
                p = []
                p.append(x)
        s += str(len(p))
        s += p[0]
        num.append(s)
    return num[n]


def countAndSay(self, n):
    s = '1'
    for i in range(n-1):
        count = 1
        temp = []
        for index in range(1, len(s)):
            if s[index] == s[index-1]:
                count += 1
            else:
                temp.append(str(count))
                temp.append(s[index-1])
                count = 1
        temp.append(str(count))
        temp.append(s[-1])
        s = ''.join(temp)
    return s


def countAndSay(self, n):
    if n == 1: return "1"
    s = self.countAndSay(n-1)
    i, ch, tmp = 0, s[0], ''
    for j in range(1, len(s)):
        if s[j] != ch:
            tmp += str(j-i) + ch
            i, ch = j, s[j]
    tmp += str(len(s)-i) + ch
    return tmp


def countAndSay(self, n):
	arr = [1]
	for i in range(n-1):
        temp = []
        count = 1 
        for i,x in enumerate(arr[1:],1):
            if arr[i-1] == x:
                count += 1
            else:
                temp.append(count)
                temp.append(arr[i-1])
                count = 1 
        temp.append(count)
        temp.append(arr[i])
            
        arr = temp
    return "".join(map(str,arr))


def count_and_say_improved(n):
	if n == 1:
		return '1'
	counter = 0
	s = '1'  # Start know one == '1'
	result = []
	for _ in xrange(n - 1):
		counter, current_val = 0, s[0]
		for v in s:
			if v == current_val:
				counter += 1
			else:
				result.append(str(counter))
				result.append(current_val)
				current_val = v
				counter = 1
		result.append(str(counter))
		result.append(current_val)
		s = "".join(result)
		result = []

	return s


def count_and_say(n):
	if n == 1:
		return '1'
	if n == 2:
		return '11'
	value = '11$'
	counter = 1
	result = []

	for i in xrange(3, n + 1):
		for j in xrange(len(value) - 1):
			if value[j] == value[j + 1]:
				counter += 1
			else:
				result.append(str(counter))
				result.append(value[j])
				counter = 1
		result.append('$')
		value = "".join(result)
		result = []

	return value[:-1]


from collections import defaultdict
class Solution:
    def countAndSay(self, n):
        count,val=1,"1"
        dict_=defaultdict(int)
        while count<n:
            newres=""
            for i in range(len(val)):
                if i==0:
                    dict_[val[i]]+=1
                else:
                    if val[i]!=val[i-1]:
                        newres+=str(dict_[val[i-1]])+val[i-1]
                        dict_=defaultdict(int)
                        dict_[val[i]]+=1
                    else:
                        dict_[val[i]]+=1
            newres+=str(dict_[val[i]])+val[i]
            val=newres
            dict_=defaultdict(int)    
            count+=1
        return val


def countAndSay(self, n):   
    def cns(str_):
        res = ''
        str_ += '#'
        c = 1
        for i in range(len(str_) - 1):
            if str_[i] == str_[i+1]:
                c += 1
                continue
            else:
                res += str(c) + str_[i]
                c = 1
        
        return res
        
    start = '1'
    for i in range(n-1):
        start = cns(start)
    return start


def countAndSay(self, n):
    if n == 1:
        return "1"
    prev = "1"
    res = ""
    for i in range(1, n):
        count = 1
        for j in range(len(prev)-1):
            if prev[j] == prev[j+1]:
                count += 1
            else:
                res += str(count)+prev[j]
                count = 1
        res += str(count)+prev[-1]
        prev = res
        res = ""
    return prev


def countAndSay(self, n):
    res = "1"
    for _ in xrange(n-1):
        res = self.helper(res)
    return res
    
def helper(self, n):
    count, i, res = 1, 0, ""
    while i < len(n) - 1:
        if n[i] == n[i+1]:
            count += 1
        else:
            res += str(count) + n[i]
            count = 1
        i += 1
    res += str(count) + n[i]
    return res




















































