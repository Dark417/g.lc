"""
040.1189. Maximum Number of Balloons
“气球” 的最大数量

Given a string text, you want to use the characters of text 
to form as many instances of the word "balloon" as possible.

You can use each character in text at most once. 
Return the maximum number of instances that can be formed.

 

Example 1:



Input: text = "nlaebolko"
Output: 1
Example 2:



Input: text = "loonbalxballpoon"
Output: 2
Example 3:

Input: text = "leetcode"
Output: 0
 

Constraints:

1 <= text.length <= 10^4
text consists of lower case English letters only.

"""

def maxNumberOfBalloons(self, text: str) -> int:
    b,a,l,o,n = map(lambda x: text.count(x), ("balon"))
    count = 0
    while True:
        if b > 0 and a > 0 and l > 1 and o > 1 and n > 0:
            count += 1
            b -= 1
            a -= 1
            l -= 2
            o -= 2
            n -= 1
        else:
            break
    return count


    return min(t.count('b'), t.count('a'), t.count('l') // 2, t.count('o') // 2, t.count('n'))
    return min(t.count(c) // int(cnt) for c, cnt in zip('balon', '11221'))
    return min(t.count(c) // 'balloon'.count(c) for c in 'balon')
    return min(text.count('b'), text.count('a'), text.count('l') // 2, text.count('o') // 2, text.count('n'))


def maxNumberOfBalloons(self, text: str) -> int:
    cnt = collections.Counter(text)
    cntBalloon = collections.Counter('balloon')
    return min([cnt[c] // cntBalloon[c] for c in cntBalloon])


def maxNumberOfBalloons(self, text: str) -> int:
    counter = {"b":0, "a":0, "l":0, "o":0, "n":0}
    for char in text:
        if char in counter:
            counter[char] += 1
    counter["l"] //= 2
    counter["o"] //= 2
    return min(counter.values())

def maxNumberOfBalloons(self, text: str) -> int:
    counter=collections.Counter(text)
    s={counter['b'],counter['a'],counter['l']//2,counter['o']//2,counter['n']}
    return min(s)     

def maxNumberOfBalloons(self, text: str) -> int:
    a = c(text)
    return min(a['l'] // 2, a['o'] // 2, a['b'], a['a'], a['n'])

def maxNumberOfBalloons(self, text):
    c = collections.Counter(text)
    return min(c["b"], c["a"], c["l"] / 2, c["o"] / 2, c["n"])

def maxNumberOfBalloons(self, text):
    x = collections.Counter(text)
    return min(x['b'], x['a'], x['l']//2, x['o']//2, x['n'])

    text_counter = Counter(text)
        return min(text_counter['b'], text_counter['a'], text_counter['l']//2, text_counter['o']//2, text_counter['n'])


def maxNumberOfBalloons(self, text: str) -> int:
        b = text.count("b")
        a = text.count("a")
        l = text.count("l")
        o = text.count("o")
        n = text.count("n")
        
        return min(b, a, l//2, o//2, n)


def maxNumberOfBalloons(self, text: str) -> int:
    # Creating a map from the string under consideration
	string = "balloon"
    sctr = Counter(string)  
    
	# Keeping only characters of interest from text
    ltext = [c for c in text if c in string]        
	
	# If we don't have any characters from 'balloon' - return 0 instantly
    if not ltext:
        return 0
		
	# Creating a map for text under consideration	
    tctr = Counter(ltext)       
    
    # If both the hashmaps are equal - then return 1
    if tctr == sctr:
        return 1
    # Then we have to calculate the actual count
    else:
        rmap = {}
        for k,v in sctr.items():
            if k == 'l' or k == 'o':
                rmap[k] = tctr[k] // 2
            else:
                rmap[k] = tctr[k]
        return min(rmap.values()) 


def maxNumberOfBalloons(self, text: str) -> int:  
    word = list('balloon')
    letter_count = collections.Counter(text)
    count = 0
    i = 1
    while i:
        for letter in word:
            if letter_count[letter]!=0:
                letter_count[letter]-=1
            else:
                i = 0
                break
        count+=1
        
    return count-1


	balloon = 'balloon'
    collon = ''
    t_len = len(text)
    
    count = 0
    
	# remove the charactor when it is found. the length of 'balloon' is 7
    while t_len >= 7:
        for i in balloon:
            if i in text:
                text = text.replace(i,'',1)
                collon = collon+i
        if collon == balloon:
            count += 1
            collon = ''
        else:
            break
        t_len = len(text)
    
    return(count)


def maxNumberOfBalloons(self, text: str) -> int:
    d = {'b': 0, 'a': 0, 'l': 0, 'o': 0, 'n': 0}

 
    for e in text:
        if e in d:
            if e == 'l' or e == 'o':
                d[e] += 0.5
            else:
                d[e] += 1
    
    return int(min(d.values()))






















