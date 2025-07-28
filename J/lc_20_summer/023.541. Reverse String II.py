"""
023.541. Reverse String II
反转字符串 II

Given a string and an integer k, you need to reverse the first k characters for every 2k characters counting from the start of the string. If there are less than k characters left, reverse all of them. If there are less than 2k but greater than or equal to k characters, then reverse the first k characters and left the other as original.
Example:
Input: s = "abcdefg", k = 2
Output: "bacdfeg"

Restrictions:
The string consists of lower English letters only.
Length of the given string and k will in the range [1, 10000]


d_note
string direct slice
calc start, end
2*k

index for iterator
incr i

when modify the same var, together
+= only one

"""


def reverseStr(self, s, k):
    i = 0
    ret = ""

    while i < len(s):
        if len(s)-i+1 >= 2*k:
            ret.join(s[i:i+k][::-1]+s[i+k:i+2k])
            i += 2*k

        elif len(s)-1-i < 2*k and len(s)-1-i >= k:
            ret.join(s[i:i+k][::-1]+s[i+k:])

        elif len(s)-1-i < k:
            ret.join(s[i:][::-])
    
    return ret


    while i < len(s):
        if len(s)-i+1 >= 2*k:

            ret = ret + "".join(s[i:i+k][::-1] + s[i+k:i+2*k])
            i += 2*k

        elif len(s)-i+1 < 2*k and len(s)-i+1 >= k:
            ret = ret + "".join(s[i:i+k][::-1]+s[i+k:])
            break
        elif len(s)-i+1 < k:
            ret = ret + "".join(s[i:][::-1])
            break
    return ret


def reverseStr(self, s: str, k: int) -> str:
    return ''.join([s[i: i + k][::-1] + s[i + k: i + 2 * k] for i in range(0, len(s), 2 * k)])
    return s[:k][::-1] + s[k:2*k] + self.reverseStr(s[2*k:], k) if s else ""
    return ''.join([s[i*k:(i+1)*k][::((-1)**(i+1))] for i in range(len(s)//k+1)])

    

def reverseStr(self, s: str, k: int) -> str:
    res = ''
	for i in range(0, len(s), 2*k):
	    res += s[i:i+k][::-1]+s[i+k:i+2*k]
	return res

def reverseStr(self, s: str, k: int) -> str:
    res=[]
    for i in range(0,len(s),2*k):
        res.append(s[i:i+k][::-1]+s[i+k:i+2*k])
    return ''.join(res)


def reverseStr(self, s: str, k: int) -> str:
    if len(s) <= k:
        return ''.join(reversed(s))
    elif k < len(s) <= 2 * k:
        return ''.join(reversed(s[:k])) + s[k:]
    else:
        return ''.join(reversed(s[:k])) + s[k:2 * k] + self.reverseStr(s[2 * k:], k)


def reverseStr(self, s: str, k: int) -> str:
    if len(s)<(k):return s[::-1]
    if len(s)<(2*k):return (s[:k][::-1]+s[k:])
    return s[:k][::-1]+s[k:2*k]+reverseStr(s[2*k:],k)



def reverseStr(self, s: str, k: int) -> str:
    left, mid, right = 0, k, 2 * k                  # 初始化左中右指针
    res = ''                                        # 初始化结果字符串
    while len(res) < len(s):                        # 满足条件时执行
        res += s[left:mid][::-1] + s[mid:right]     # 把当前单元的结果添加到结果字符串
        left, mid, right = left + 2 * k, mid + 2 * k, right + 2 * k                          
    return res                                      # 返回结果


def reverseStr(self, s: str, k: int) -> str:
    i,j = 0,2*k
    ans = ''
    while i<=len(s) and j<=len(s):
        ans += s[i:i+k][::-1]+s[i+k:j]
        i += 2*k
        j += 2*k
    if len(s[i:])<=k:
        ans += s[i:][::-1]
    elif k<len(s[i:])<2*k:
        ans += s[i:i+k][::-1]+ s[i+k:]
    return ans



def reverseStr(self, s, k):
    res = ''
    for i in xrange(0, len(s), k):
        idx = min(i+k, len(s))
        if (i/k) & 1 == 0:
            res += s[i:idx][::-1]
        else:
            res += s[i:idx]

    return res


def reverseStr(self, s, k):                
	# Divide s into an array of substrings length k
	s = [s[i:i+k] for i in range(0, len(s), k)]
	# Reverse every other substring, beginning with s[0]
    for i in range(0, len(s), 2):
        s[i] = s[i][::-1]
	# Join array of substrings into one string and return 
    return ''.join(s)


def reverseStr(self, s, k):
    s = list(s)
    for i in xrange(0, len(s), 2*k):
        s[i:i+k] = reversed(s[i:i+k])
    return "".join(s)


def reverseStr(self, s, k):
    news = ''
    n = (len(s) // (2 * k)) * 2 * k
    for i in range(0, n, 2 * k):
        news += s[i:i + k][::-1]
        news += s[i + k:i + 2 * k]
    if len(s) - n < k:
        news += s[n:][::-1]
    else:
        news += s[n:n + k][::-1]
        news += s[n + k:]
    return news
    

def reverseStr(self, s: str, k: int) -> str:
    L = len(s)
    if L<k: return s[::-1]
    if L>k and L<=k*2:
        return s[:k][::-1]+s[k:]
    ans = ''
    for i in range(0,L,2*k):
        ans+=(s[i:i+k][::-1]+s[i+k:i+2*k])
    return ans

    


    


    

    


    


    


    


    


    

    


    


    


    


    


    