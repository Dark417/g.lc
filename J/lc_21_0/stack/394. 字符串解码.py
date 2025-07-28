# 394. 字符串解码

def decodeString(self, s: str) -> str:
    stack = []

    for c in s:
        if c != "]":
            stack.append(c)
        else:
            tmp = ""
            while stack[-1] != "[":
                tmp = stack.pop(-1) + tmp
            stack.pop(-1)
            times = ""
            while stack and stack[-1].isdigit():
                times = stack.pop(-1) + times
            times = int(times)
            
            tmp = "".join(tmp for _ in range(times))
            for t in tmp:
                stack.append(t)
    return "".join(stack)


def decodeString(self, s: str) -> str:
	stack = []
	stack_n = []
	ans = ""
	cur = 0
	for c in s:
		if c.isdigit():
			cur = cur*10 + int(c)
		elif c == "[":
			stack.append(ans)
			stack_n.append(cur)
			cur = 0
			ans = ""
		elif c == "]":
			ans = stack.pop() + stack_n.pop() * ans
		else:
			ans += c
	return ans

def decodeString(self, s):
    stack = []; curNum = 0; curString = ''
    for c in s:
        if c == '[':
            stack.append(curString)
            stack.append(curNum)
            curString = ''
            curNum = 0
        elif c == ']':
            num = stack.pop()
            prevString = stack.pop()
            curString = prevString + num*curString
        elif c.isdigit():
            curNum = curNum*10 + int(c)
        else:
            curString += c
    return curString
    

def decodeString(self, s: str) -> str:
    stack, res, multi = [], "", 0
    for c in s:
        if c == '[':
            stack.append([multi, res])
            res, multi = "", 0
        elif c == ']':
            cur_multi, last_res = stack.pop()
            res = last_res + cur_multi * res
        elif '0' <= c <= '9':
            multi = multi * 10 + int(c)            
        else:
            res += c
    return res


def decodeString(self, s: str) -> str:
    def dfs(s, i):
        res, multi = "", 0
        while i < len(s):
            if '0' <= s[i] <= '9':
                multi = multi * 10 + int(s[i])
            elif s[i] == '[':
                i, tmp = dfs(s, i + 1)
                res += multi * tmp
                multi = 0
            elif s[i] == ']':
                return i, res
            else:
                res += s[i]
            i += 1
        return res
    return dfs(s,0)





3[z]   2[  2[y]  pq4[2[jk] e1[f]]  ] ef

zzzyy
pqjkjkef

zzzyypqjkjkef

zzzyypqjkjkefzzzyypqjkjkefzzzyypqjkjkefzzzyypqjkjkefzzzyypqjkjkefzzzyypqjkjkefef






def decodeString(self, s):
    stack = []
    stack.append(["", 1])
    num = ""
    for ch in s:
        if ch.isdigit():
          num += ch
        elif ch == '[':
            stack.append(["", int(num)])
            num = ""
        elif ch == ']':
            st, k = stack.pop()
            stack[-1][0] += st*k
        else:
            stack[-1][0] += ch
    return stack[0][0]


def decodeString(self, s):
    stack = []
    stack.append([[], 1])
    num = []
    for ch in s:
        if ch.isdigit():
            num.append(ch)
        elif ch == '[':
            stack.append([[], int("".join(num))])
            num = []
        elif ch == ']':
            st, k = stack.pop()
            stack[-1][0].extend(st*k)
        else:
            stack[-1][0].append(ch)
    return "".join(stack[0][0])


# problem
def decodeString(self, s: str) -> str:
    stack = []
    stack_t = []
    word = ""
    t = ""
    cur = ""
    for c in s:
        if c.isdigit():
            t += c
        elif c == "[":
            stack_t.append(int(t))
            t = ""
            if word:
                stack.append(word)
                word = ""
        elif c == "]":
            pre = stack.pop() if stack else ""
            time = stack_t.pop()
            
            word = pre + time * word
            # if word:
            stack.append(word)
            
        else:
            word += c
    print(stack)
    return "".join(stack) + word





def decodeString(self, s: str) -> str:
    stack=list()
    length=len(s)
    i=length-1
    while i>=0:
        if s[i].isdigit()==False:
            stack.append(s[i])
            i-=1
        else:
            num=''
            while i>=0 and s[i].isdigit():
                num=s[i]+num
                i-=1
            sub=''
            while stack[-1]!=']':
                tmp=stack.pop()
                if tmp!='[':
                    sub+=tmp
            stack.pop()#弹出']'
            sub=int(num)*sub
            stack.append(sub)

    stack.reverse()
    return ''.join(stack)



def decodeString(self, s: str) -> str:
    self.brasket_index = self.get_brasket_index(s)
    return self.decode(s, 0, len(s))

def decode(self, s, left, rightEnd):
    res = ""
    i = left 
    while i < rightEnd:
        c = s[i]
        if c.isalpha():
            res += c
            i += 1 
        else: # isnumeric
            number = 0
            while s[i].isnumeric():
                number = number * 10 + int(s[i])
                i += 1
            res += number * self.decode(s, i+1, self.brasket_index[i])
            i = self.brasket_index[i] + 1
    return res 
    
def get_brasket_index(self, s):
    brasket_index = {}
    stk = []
    for i, c in enumerate(s):
        if c == '[':
            stk.append(i)
        elif c == ']':
            brasket_index[stk.pop()] = i 
    return brasket_index











