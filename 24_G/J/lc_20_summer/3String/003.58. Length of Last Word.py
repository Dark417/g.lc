"""
003.58. Length of Last Word
Given a string s consists of upper/lower-case alphabets and empty space characters ' ',
return the length of last word (last word means the last appearing word if we loop from left to right) in the string.

If the last word does not exist, return 0.

Note: A word is defined as a maximal substring consisting of non-space characters only.

Example:

Input: "Hello World"
Output: 5

"""

def lengthOfLastWord(self, s: str) -> int:

    return len(s.rstrip().split(" ")[-1])
    return len(s.strip().split(" ")[-1])

    return len(s.strip().split()[-1]) if len(s.strip()) > 0 else 0
    return len(s.split()[-1]) if s.strip() else 0


def lengthOfLastWord(self, s):
    l = s.strip()
    if not l:
        return 0
    else:
        return len(l.split()[-1])

    # one line
    if not s: return 0


def lengthOfLastWord(self, s):
    wordlist = s.split()
    if wordlist:
        return len(wordlist[-1])
    return 0


def lengthOfLastWord(self, s: str) -> int:
    s=s.split()
    return len(s[-1]) if s else 0


def lengthOfLastWord(self, s):
    s = s.strip()
    if len(s) != 0:
        return len(s.split(' ')[-1])
    else:
        return 0

###

def lengthOfLastWord(self, s: str) -> int:
    s = s.rstrip()
    if s.count(' ') == 0:
        return len(s)
    x = 0
    while True:
        if s[-(x+1)] == ' ':
            return x
        x += 1

def lengthOfLastWord(self, s: str) -> int:
    s = s.rstrip()
    n = len(s)
    for i in range(n - 1, -1, -1):
        if s[i] == ' ':
            return n - 1 - i
    return n


###
def lengthOfLastWord(self, s: str) -> int:
    try:
        a = len(s.split()[-1])
        return a
    except:
        return 0





def lengthOfLastWord(self, s: str) -> int:
    if not s:
        return 0
    count = 0
    flag = 0
    for i in s[::-1]:
        if i is " " and flag == 0:
            continue
        if i is not " ":
            count += 1
            flag = 1
        else:
            break
    return count

    # for i in range (0,len(s)):
    # 对空字符串进行判断
    if len(s) == 0:
        return 0
    k = 0
    maxlenth = 0
    while k < len(s):
        l = 0
        # 当不是字符时，进行的处理
        if not s[k].isalpha():
            # print("wobushi")
            k += 1
            continue
        else:
            # 当检测的字符是字母时，l为计数器
            for i in range(k, len(s)):
                if s[i].isalpha():
                    l += 1
                    maxlenth = l

                    # print(maxlenth)
                else:

                    # print(k)
                    break
        k = k + l
    return maxlenth


def lengthOfLastWord(self, s: str) -> int:
    if s.split()==[]:
        return 0
    else:
        s=s.split()
        return len(s[-1])
