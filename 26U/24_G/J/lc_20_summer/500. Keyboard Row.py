"""
500. Keyboard Row

Given a List of words, return the words that can be typed using letters of alphabet on only one row's of American keyboard like the image below.

Example:

Input: ["Hello", "Alaska", "Dad", "Peace"]
Output: ["Alaska", "Dad"]


Note:

You may use one character in the keyboard more than once.
You may assume the input string will only contain letters of alphabet.
"""
input0 = ["Hello", "Alaska", "Dad", "Peace"]


# regexp
def findWords(self, words):
    return filter(re.compile('(?i)([qwertyuiop]*|[asdfghjkl]*|[zxcvbnm]*)$').match, words)


# set

def findWords(self, words):
    a=set('qwertyuiop')
    b=set('asdfghjkl')
    c=set('zxcvbnm')
    ans=[]
    for word in words:
        t=set(word.lower())
        if a&t==t:
            ans.append(word)
        if b&t==t:
            ans.append(word)
        if c&t==t:
            ans.append(word)
    return ans

    for word in words:
        w = set(word.lower())
        if (w & a == w) | (w & b == w) | (w & c == w):
            ans.append(word)
    return ans

def findWords(self, words):
    qwer = set("qwertyuiop")
    asdf = set("asdfghjkl")
    zxcv = set("zxcvbnm")
    ans = []

    for word in words:
        w = set(word.lower())
        if w <= qwer or w <= asdf or w <= zxcv:
            ans.append(word)
    return ans


def findWords(self, words):
    row1 = set('QWERTYUIOP')
    row2 = set('ASDFGHJKL')
    row3 = set('ZXCVBNM')

    wordList = []

    for word in words:
        string = set(word.upper())
        for charSet in [row1, row2, row3]:
            if string & charSet == string:
                wordList.append(word)
                break

    return wordList


def findWords(words):
    first_row = set('qwertyuiop')
    second_row = set('asdfghjkl')
    last_row = set('zxcvbnm')
    res = []
    for w in words:
        if set(w.lower()).issubset(first_row) or set(w.lower()).issubset(second_row) or set(w.lower()).issubset(last_row):
            res.append(w)
    return res


def findWords(self, words):
    rst = []
    a, b, c = set("qwertyuiop"), set("asdfghjkl"), set("zxcvbnm")
    for word in words:
        cur = set(word.lower())
        if not (cur - a) or not (cur - b) or not (cur - c):
            rst.append(word)
    return rst


def findWords(self, words):
    keyboards = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
    ans = []
    for w in words:
        if any(set(w.lower()) <= set(r) for r in keyboards):
            ans.append(w)

    return ans


def findWords(self, words):
    first, second, third = set("qwertyuiopQWERTYUIOP"), set("asdfghjklASDFGHJKL"), set("zxcvbnmZXCVBNM")
    return [word for word in words if
            all(c in first for c in word) or all(c in second for c in word) or all(c in third for c in word)]


#
def findWords(self, words):
    line1, line2, line3 = set('qwertyuiop'), set('asdfghjkl'), set('zxcvbnm')
    ret = []
    for word in words:
        w = set(word.lower())
        if w <= line1 or w <= line2 or w <= line3:
            ret.append(word)
    return ret


def findWords(self, words):
    return filter(lambda word:
                  set(word.lower()) - set("qwertyuiop") == set() or
                  set(word.lower()) - set("asdfghjkl") == set() or
                  set(word.lower()) - set("zxcvbnm") == set(),
                  words)


#
def lamda_any(words):
    r1 = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p']
    r2 = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l']
    r3 = ['z', 'x', 'c', 'v', 'b', 'n', 'm']
    is_true = lambda word: any(
        [all(i in r1 for i in word.lower()), all(i in r2 for i in word.lower()), all(i in r3 for i in word.lower())])
    return list(filter(is_true, words))


# D
def ifWordInLine(word, line):
    for char in word:
        if char in line:
            continue
        else:
            return False
    return True


def findWords(words):
    res = []

    l1 = "qwertyuiop"
    l2 = "asdfghjkl"
    l3 = "zxcvbnm"
    key = [l1, l2, l3]
    keyboard = []

    for l in key:
        line = [i for i in l]
        # line += [i.upper() for i in line]
        keyboard.append(line)

    for word in words:
        word_lower = word.lower()

        for line in keyboard:
            if ifWordInLine(word_lower, line):
                res.append(word)

    return res


res = findWords(input0)
print(res)
