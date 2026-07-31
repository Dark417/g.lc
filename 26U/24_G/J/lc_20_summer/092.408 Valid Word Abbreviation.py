"""
092.408	Valid Word Abbreviation
有效单词缩写

给一个 非空 字符串 s 和一个单词缩写 abbr ，判断这个缩写是否可以是给定单词的缩写。

字符串 "word" 的所有有效缩写为：

["word", "1ord", "w1rd", "wo1d", "wor1", "2rd", "w2d", "wo2", "1o1d", "1or1", "w1r1", "1o2", "2r1", "3d", "w3", "4"]
注意单词 "word" 的所有有效缩写仅包含以上这些。任何其他的字符串都不是 "word" 的有效缩写。

注意:
假设字符串 s 仅包含小写字母且 abbr 只包含小写字母和数字。

示例 1:

给定 s = "internationalization", abbr = "i12iz4n":

函数返回 true.
 

示例 2:

给定 s = "apple", abbr = "a2e":

函数返回 false.



"""

#
a = "i12iz4n5"
cur = ""
l = []
for x, i in enumerate(a):
	if i.isdigit():
		cur += i
		if x < len(a)-1 and a[x+1].isalpha() or x == len(a)-1:
			l.append(int(cur))
			cur = ""
	else:
		l.append(i)


# D
"""

"""
def validWordAbbreviation(self, word: str, abbr: str) -> bool:  
    l = []
    cur = ""
    for x, i in enumerate(abbr):
        if i.isdigit():
            if cur == "" and int(i) == 0:
                return False
            else:
                cur += i
                if x < len(abbr)-1 and abbr[x+1].isalpha() or x == len(abbr)-1:
                    l.append(int(cur))
                    cur = ""
                
        else:
            l.append(i)
    i = 0
    j = 0
    if sum([i if type(i) == int else 1 for i in l]) != len(word):
        return False

    while i < len(word):
        if type(l[j]) == int:
            if l[j] > len(word[i:]) or l[j] == 0:
                return False
            else:
                i += l[j]
                j += 1
                continue
        else:
            if word[i] != l[j]:
                return False
            else:
                i += 1
                j += 1
    return True






# Chopper
def validWordAbbreviation1(self, word: str, abbr: str) -> bool:
    i = 0
    j = 0
    m = len(word)
    n = len(abbr)
    while i < m and j < n:
        if abbr[j].isdigit():
            if abbr[j] == "0": return False

            # inner loop get a sequence as INT
            num = 0
            while j < n and abbr[j].isdigit():
                num = num * 10 + int(abbr[j])
                j += 1
            i += num
        else:
            if word[i] != abbr[j]:
                return False
            i += 1
            j += 1
    return i == m and j == n 		# classic check




def validWordAbbreviation(self, word: str, abbr: str) -> bool:
    m = len(word)
    p = 0
    num = 0
    for a in abbr:
        if a.isdigit():
            if num == 0 and a == "0": return False
            num = num * 10 + int(a)
        else:
            p += num
            if p >= m or word[p] != a: return False
            num = 0
            p += 1
    return p + num == m



def validWordAbbreviation(self, word: str, abbr: str) -> bool:
    count = i = j = 0
    while i < len(word) and j < len(abbr):
        while j < len(abbr) and abbr[j].isdigit():
            if abbr[j] == '0' and count == 0:
                return False
            count = count*10 + int(abbr[j])
            j += 1
        
        if count > 0:
            i += count
            count = 0
        elif word[i] == abbr[j]:
            i += 1
            j += 1
        else:
            return False
    return count == len(word)-i and j == len(abbr)



# 将abbr转换为含通配符*的字符串
def validWordAbbreviation(self, word: str, abbr: str) -> bool:
    abbr += '#'
    b = ""
    num = 0
    for i in range(len(abbr)):
        if abbr[i] == '0' and num == 0:
            return False
        if abbr[i].isdigit():
            num = num * 10 + int(abbr[i])
        else:
            if num > len(word):
                return False
            b += num * '*' + abbr[i]
            num = 0
    b = b[:len(b) - 1]
    if len(word) != len(b):
        return False
    for i in range(len(word)):
        if word[i] ！= b[i] and b[i] == '*'
            return False
    return True



def validWordAbbreviation(self, word, abbr):
    p = q = 0
    size1 = len(word)
    size2 = len(abbr)
    while p < size1 and q < size2:
        if word[p] != abbr[q]:
            cnt = 0
            while q < size2 and abbr[q].isdigit():
                cnt += 1
                q += 1
            if cnt:
                if abbr[q-cnt] == '0':
                    return False
                p += int(abbr[q-cnt: q])
            else:
                return False
        else:
            p += 1
            q += 1
    return p == size1 and q == size2



def validWordAbbreviation(self, word: str, abbr: str) -> bool:
    w,a=0,0
    num=0
    while w<len(word) and a<len(abbr):
        if word[w]==abbr[a]:
            w+=1
            a+=1
        elif not word[w]==abbr[a] and abbr[a].isalpha():
            return False
        elif abbr[a]=="0":  #数字打头不为0
            return False
        else:
            while a<len(abbr) and abbr[a].isdigit():
                num=num*10+int(abbr[a])
                a+=1
            w+=num
            num=0   #记得归零
    return w==len(word) and a==len(abbr)    #保证到尾，没有剩余



def validWordAbbreviation(self, word: str, abbr: str) -> bool:
    # 维护tmp（过程有些繁琐，能力有限）
    tmp = ''
    i = 0
    while i < len(abbr):
        if abbr[i] == '0':  # 处理测试案例里有0的情况
            tmp += abbr[i]
            i += 1
        elif abbr[i].isalpha():  # 是字母直接加到tmp中
            tmp += abbr[i]
            i += 1
        else:
            # 如果abbr = a13b，这里的数字表示13，而不是1和3，所以如果是数字还要考虑下一位是不是数字
            if i < len(abbr)-1 and not abbr[i].isalpha() and not abbr[i+1].isalpha(): 
                tmp += '*' * int(abbr[i] + abbr[i+1])
                i += 2
            else:
                tmp += '*' * int(abbr[i])
                i += 1
    # 将tmp与word比较
    if len(tmp) != len(word): # 长度不等直接返回False
        return False
    else:
        for j in range(len(tmp)):
            if tmp[j] != '*' and tmp[j] != word[j]:  # 只比较非*部分
                return False
    
    return True
























