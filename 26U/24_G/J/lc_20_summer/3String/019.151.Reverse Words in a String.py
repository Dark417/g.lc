"""
019.151.Reverse Words in a String
翻转字符串里的单词


Given an input string, reverse the string word by word.

 

Example 1:

Input: "the sky is blue"
Output: "blue is sky the"
Example 2:

Input: "  hello world!  "
Output: "world! hello"
Explanation: Your reversed string should not contain leading or trailing spaces.
Example 3:

Input: "a good example"
Output: "example good a"
Explanation: You need to reduce multiple spaces between two words to a single space in the reversed string.


"""


def reverseWords(self, s):

        l = s.split()
        return "".join(i + " " for i in l[::-1]).strip()

        return "".join(i + " " for i in s.split()[::-1]).strip()

        return " ".join(s.strip().split()[::-1])
        return " ".join(s.split()[::-1])
        [-1::-1]
        
        return " ".join(reversed(s.strip().split()))
        return " ".join(reversed(s.split()))

def reverseWords(self, s):

    l = s.strip().split()
    i = len(l)-1
    ret = ""
    while i >= 0:
        ret += l[i] 
        ret += " "
        i -= 1
    #ret = ret[:-1]
    return ret.strip()


def reverseWords(self, s):
    s = list(" ".join(s.split()))[::-1]
    i = 0 
    while i < len(s):
        start = i 
        while i < len(s) and not s[i].isspace():
            i += 1
        self.reverse(s, start, i-1)
        i += 1
    return "".join(s)


def reverse(self, s, i, j):
    while i < j:
        s[i], s[j] = s[j], s[i]
        i += 1; j -= 1


def reverseWords(self, s: str) -> str:
        res = ""
        s = " " + s + " "
        start = end = -1
        for i in range(len(s) - 2, 0, -1):
            if s[i + 1] == " " and s[i] != " ":
                end = i
            if s[i - 1] == " " and s[i] != " ": 
                start = i
                res = res + " " + s[start: end + 1]
        return res[1:]


def reverseWords(self, s):
    # First reverse entire string, then iterate over reversed string
    # and again reverse order of characters within a word. Append each word to words.
    word = ""
    words = ""
    s = s[::-1]
    for j, i in enumerate(s):
        # character is not space, a current word exists, 
        # and previous character is space, e.g. i=b in " a b":
        if i != " " and word != "" and s[j-1] == " ":
            # add current word to words and append " " to later add this i
            words += (word + " ")
            word = i
        # character is not space, but it's either first character in string
        # or is part of current word, e.g. i=b in "b", " b" "ab", "a ab "
        elif i != " ":
            word = i + word
        else:
            continue

    words += word
    
    return(words)


def reverseWords(self, s: str) -> str:
    data = s.strip()
    start, end = 0, len(data)
    words = []
    while start < end:
        word = []
        
		# Traverse the string till it find a character and increment the index variable
        while start < end and data[start] == " ":
            start += 1

		# Traverse the string till it find space and append the character in word list
        while start < end and data[start] != " " :
            word.append(data[start])
            start += 1
        
		# Convert the list to string using join and append it to words list
        str_word = "".join(word)
        words.append(str_word)
      
	  
    return " ".join(words[::-1])


def reverseWords(self, s):
	words = []
    word_so_far = []
    for ch in s:
        if ch != ' ':
            word_so_far.append(ch)
        else:
            # Avoid adding empty words when encountered multiple spaces.
            if word_so_far: 
                words.append(''.join(word_so_far))
                word_so_far = []  # Reset


def reverseWords(self, s):        
    a = s.strip().split(" ")    
    b = []
    for i in a:
        if i != "":
            b.insert(0,i)      
    return ' '.join(b)



def reverseWords(self, s: str) -> str:
    if not s:
        return ''
    
    start = 0
    c = s[0]
    
    while start < len(s) and s[start] == ' ':
        start += 1
        
    if start == len(s):
        return ''

    end = len(s) - 1
    
    while s[end] == ' ':
        end -= 1
            
    l = []
    spaces = 0
    
    for c in s[start:end+1]:
        if c == ' ':
            if spaces == 1:
                continue
            else:
                spaces += 1
        else:
            spaces = 0
            
        l.append(c)
        
    start = 0
    end = len(l) - 1
    
    while start < end:
        l[start], l[end] = l[end], l[start]
        start += 1
        end -= 1
    
    
    start = 0
    end = len(l) - 1
    i = start
    prev = 0
    
    while i <= end:
        while i <= end and l[i] != ' ':
            i += 1
            
        if prev <= end:
            m = prev
            n = i-1
            
            while m < n:
                l[m], l[n] = l[n], l[m]
                m += 1
                n -= 1
            
            prev = i+1
            i += 1
    
    return ''.join(l)
















