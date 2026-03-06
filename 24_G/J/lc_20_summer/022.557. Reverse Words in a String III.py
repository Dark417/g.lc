"""
022.557. Reverse Words in a String III
反转字符串中的单词 III

Given a string, you need to reverse the order of characters in each 
word within a sentence while still preserving whitespace and initial word order.

Example 1:
Input: "Let's take LeetCode contest"
Output: "s'teL ekat edoCteeL tsetnoc"
Note: In the string, each word is separated by single space and 
there will not be any extra space in the string.




"""

def reverseWords(self, s):
    l = s.strip().split()
    return " ".join(i[::-1] for i in l)

    return " ".join(i[::-1] for i in s.split())
    return " ".join(s.split()[::-1])[::-1]

    return " ".join(reversed(s.split(' ')))[::-1]
    return " ".join(''.join(reversed(s)).split()[::-1])
    return " ".join("".join(reversed(x)) for x in s.split())
    #return " ".join(["".join(reversed(x)) for x in s.split()])


    return s.split.map(&:reverse).join(" ")

    return " ".join(map(lambda x: x[::-1], s.split()))



    terms = s.split(' ')
        for i in range(len(terms)):
            # 字符串反转
            terms[i] = terms[i][::-1]
        # 将数组拼接为字符串
        return ' '.join(terms)


	for i in range(len(s)):
	    m=s[i][::-1]
	    y.append(m)


	 s = s.split()
	for i in range(len(s)): s[i] = s[i][::-1]
	return " ".join(s)


def reverseWords(self, s):







#stack
def reverseWords(self, s: str) -> str:
    stack, res, s = [], "", s + " "
    for i in s:
        stack.append(i)
        if i == " ":
            while(stack):
                res += stack.pop()
    return res[1:]


def reverseWords(self, s: str) -> str:
        j = 0 ## 慢指针
        for i in range(len(s)):
            if s[i]==' ': ## 慢指针触发
                s = s[:j]+s[j:i][::-1]+s[i:] #业务代码
                j = i+1
            elif i ==len(s)-1: ## 业务代码
                s = s[:j]+s[j:][::-1]
        return s  


def reverseWords(self, s):
        arr=s.split(' ')
        rev_arr=[]
        str_result=[]
        for item in arr:
            for i in range(len(item)):
                rev_arr.append(item[len(item)-i-1])
            word=''.join(rev_arr)
            rev_arr=[]
            str_result.append(word)
        result=' '.join(str_result)
        return result


def reverseWords(self, s: str) -> str:
    res = ''
    tmp = ''
    for x in s:
        if x != ' ': tmp = x + tmp
        else: res += (tmp + x); tmp = ''
    if tmp: res += tmp
    return res


def reverseWords(self, s: str) -> str:
    ss = s.split(" ")
    result = []
    for iterm in ss:
        tt = []
        for i in range(len(iterm)-1, -1, -1):
            tt.append(iterm[i])
        result.append(''.join([i for i in tt]))
    return ' '.join([i for i in result])



def reverseWords(self, s):
        s = list(s)
        l = 0
        r = 0
        while r < len(s):
            while r < len(s) and s[r] != ' ':
                r += 1
            temp = r
            r -= 1
            while l < r:
                s[l], s[r] = s[r], s[l]
                l += 1
                r -= 1
            l = temp + 1
            r = temp + 1
        return ''.join(s)


def reverseWords(self, s: str) -> str:
        split=re.findall(r'\S+|\s+',s)
        for i in range(0,len(split),2):
            split[i]=split[i][::-1]
        return ''.join(split)


def reverseWords(self, s: str) -> str:
        # 得到将字符串用空格分割之后的列表
        list1 = s.split(' ')
        # 循环列表中的每一个字符串，用切片翻转
        for index, value in enumerate(list1):
            list1[index] = value[::-1]
        # 将列表重新集合成字符串
        return ' '.join(list1)


def reverseWords(self, s):
        """
        :type s: str
        :rtype: str
        """
        s = s.split(' ')
        result = []
        for i in range(len(s)):
            result.append(''.join(self. reverseWord(list(s[i]))))
        return ' '.join(result)
    def reverseWord(self, word):
        start = 0
        end = len(word) - 1
        while start < end:
            temp = word[start]
            word[start] = word[end]
            word[end] = temp
            start += 1
            end -= 1
        return word


def reverseWords(self, s: str) -> str:
        if not s: return s
        space_index, last_space = 0, -1
        ls = list(s)
        while space_index <= len(ls):
            if space_index == len(ls) or ls[space_index] == ' ':
                for i in range(1,  1 + (space_index - last_space) >> 1):
                    ls[i + last_space], ls[space_index - i] = ls[space_index - i], ls[i + last_space]
                last_space = space_index 
                space_index += 1
            else:
                space_index += 1
        return ''.join(ls)



def reverseWords(self, s: str) -> str:
        # 现将单词逐个取出来，然后选择
    left = 0
    res = ""
    for i in range(len(s)):
        if s[i] == " ":
            res += s[left:i][::-1]   # 可以用 [::-1] 但是 reversed 无法作用于字符串
            res += " "
            left = i+1
    res += s[left:][::-1]
    return res


    for i in s:
            i=i[::-1]
            fina=fina+i+' '
        return fina[:len(fina)-1] 

        #res[:-1]


def reverseWords(self, s: str) -> str:
    word_list = s.split(' ')
    for i in range(len(word_list)):
        char_list = list(word_list[i])
        char_list.reverse()
        word_list[i] = ''.join(char_list)
    return ' '.join(word_list)


def reverseWords(self, s):
    s=s+" "
    stack,res=[],""
    for word in s:
        stack.append(word)
        if word == " ":
            while stack:
                res += stack.pop()
    return res[1:]


def reverseWords(self, s: str) -> str:
    # turn the string into a list
    s = [i for i in s]
    
    start, end = 0, 0
    while end < len(s): 
        while s[end] != " " and end != len(s) - 1:
            end += 1
        
        # set end to the letter right before the space
        if end == len(s) - 1:
            right = len(s) - 1
        else:
            right = end - 1
        left = start
        # swap them
        while left < right:
            temp = s[left]
            s[left] = s[right]
            s[right] = temp
            left += 1
            right -= 1
        start = end + 1
        end = end + 1
    
    return "".join([i for i in s])



















































