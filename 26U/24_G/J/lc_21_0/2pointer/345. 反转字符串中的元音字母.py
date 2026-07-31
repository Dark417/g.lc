"""
002.345. Reverse Vowels of a String
Write a function that takes a string as input and reverse only the vowels of a string.

Example 1:

Input: "hello"
Output: "holle"
Example 2:

Input: "leetcode"
Output: "leotcede"
Note:
The vowels does not include the letter "y".


"""


def reverseVowels(self, s: str) -> str:
    dic = {'a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'}
    lst = list(s)
    n = len(s)
    l, r = 0, n - 1

    while l < r:
        if lst[l] in dic and lst[r] in dic:
            lst[l], lst[r] = lst[r], lst[l]
            l = l + 1
            r = r - 1
        elif lst[l] not in dic:
            l = l + 1
        elif lst[r] not in dic:
            r = r - 1

    return ''.join(lst)


        
def reverseVowels(self, s):
    """
    :type s: str
    :rtype: str
    """
    lstr = list(s)
    lv = []
    vow = "aeiouAEIOU"

    for i in range(len(lstr)):
        if lstr[i] in vow:
            lv.append(lstr[i])
            lstr[i] = "none"

    for i in range(len(lstr)):
        if lstr[i] == "none":
            lstr[i] = lv.pop()

    return "".join(lstr)



def reverseVowels(self, s):
    vowels = re.findall('(?i)[aeiou]', s)
    return re.sub('(?i)[aeiou]', lambda m: vowels.pop(), s)


def reverseVowels(self, s):
    return re.sub('(?i)[aeiou]', lambda m, v=re.findall('(?i)[aeiou]', s): v.pop(), s)


def reverseVowels(self, s):
    vowels = (c for c in reversed(s) if c in 'aeiouAEIOU')
    return re.sub('(?i)[aeiou]', lambda m: next(vowels), s)


def reverseVowels(self, s: str) -> str:
    vowels = re.findall('(?i)[aeiou]', s)
    return re.sub('(?i)[aeiou]', lambda x: vowels.pop(), s)


def reverseVowels(self, s):
    s = list(s)
    vows = set('aeiouAEIOU')
    l, r = 0, len(s) - 1
    while l <= r:
        while l <= r and s[l] not in vows: l += 1
        while l <= r and s[r] not in vows: r -= 1
        if l > r: break
        s[l], s[r] = s[r], s[l]
        l, r = l + 1, r - 1
    return ''.join(s)


def reverseVowels(self, s: str) -> str:
    s = list(s)
    vowels = set(['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'])
    i, j = 0, len(s) - 1

    while i < j:
        if s[i] not in vowels:
            i += 1
            continue

        if s[j] not in vowels:
            j -= 1
            continue

        s[i], s[j] = s[j], s[i]
        i += 1
        j -= 1

    return ''.join(s)


def reverseVowels(self, s: str) -> str:
    li, i, j, v = list(s), 0, len(s) - 1, set('aeiouAEIOU')
    while i < j:
        if li[i] in v and li[j] in v:
            li[i], li[j] = li[j], li[i]
            i, j = i + 1, j - 1
            continue
        if li[i] not in v: i += 1
        if li[j] not in v: j -= 1
    return ''.join(li)

# li[i] in v, li[j] in v this not constant time operation. It is better to use set() here.


def reverseVowels(self, s):
    s = list(s)
    vowel = []
    for i in s:
        if i.lower() in ('a', 'e', 'i', 'o', 'u'):
            vowel.append(str(i))
    # print vowel
    vl = len(vowel)

    for i in range(len(s)):
        if s[i].lower() in ('a', 'e', 'i', 'o', 'u'):
            s[i] = vowel[vl - 1]
            vl = vl - 1

    return ''.join(s)


def reverseVowels(self, s):
    """
    :type s: str
    :rtype: str
    """
    vowels = 'aeiouAEIOU'
    vpos = [i for i, j in enumerate(s) if j in vowels]
    svrev = list(s)
    i, j = 0, len(vpos) - 1
    while i < j:
        svrev[vpos[i]], svrev[vpos[j]] = svrev[vpos[j]], svrev[vpos[i]]
        i += 1
        j -= 1
    return ''.join(svrev)


def reverseVowels(self, s: str) -> str:
    i,j,v,a=0,len(s)-1,set("aeouiAEOUI"),list(s)
    while i<j:
        if a[i] in v and a[j] in v: a[i],a[j],i,j = a[j],a[i],i+1,j-1 #both letters are vowels, reasign a[i] with a[j], also increment i, decrement j
        elif a[j] in v: i+=1 #only a[j] are vowel then we need increment i
        else: j-=1 #in other case decrement j
    return "".join(a)


def reverseVowels(self, s: str) -> str:
    vowels = list(filter(lambda x : x in 'aeiouAEIOU', s))
    return ''.join(x if x not in 'aeiouAEIOU' else vowels.pop() for x in s)


def reverseVowels(self, s: str) -> str:
    s, t, v = list(s), s, set('aeiouAEIOU')
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] in v:
            while t[j] not in v: j -= 1
            s[i], s[j] = t[j], t[i]
            j -= 1
        i += 1
    return ''.join(s)


def reverseVowels(self, s):
    vowels = {'a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'}
    string_list = [x for x in s]
    l, r = 0, len(s) - 1
    while l <= r:
        while l < len(string_list) - 1 and string_list[l] not in vowels:
            l += 1
        while r > 0 and string_list[r] not in vowels:
            r -= 1
        if l > r:
            break
        string_list[l], string_list[r] = string_list[r], string_list[l]
        l += 1
        r -= 1
    return "".join(string_list)


def reverseVowels(self, s: str) -> str:
    vowels = set(['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'])
    left = 0
    right = len(s) - 1
    slist = list(s)

    while left < right:
        if slist[left] in vowels and slist[right] in vowels:
            slist[left], slist[right] = slist[right], slist[left]
            left += 1
            right -= 1
        elif slist[left] in vowels:
            right -= 1
        elif slist[right] in vowels:
            left += 1
        else:
            left += 1
            right -= 1

    return ''.join(slist)


def reverseVowels(self, s):
    """
    :type s: str
    :rtype: str
    """
    vowels = []
    index = []
    l = list(s)
    for i in xrange(len(l)):
        if l[i] in 'aeiouAEIOU':
            vowels.append(l[i])
            index.append(i)
    for i in index:
        l[i] = vowels.pop()
    return "".join(l)


def reverseVowels(self, s):
    arr = list(s)
    l = 0
    r = len(arr) - 1
    while l < r:
        while l < r and (arr[l] not in "aeiouAEIOU"):
            l += 1
        while l < r and (arr[r] not in "aeiouAEIOU"):
            r -= 1
        if l < r:
            arr[l], arr[r] = arr[r], arr[l]
            l += 1
            r -= 1
    return "".join(arr)


def reverseVowels(self, s):
    l = list(s)
    rev = []
    idx = []
    index = 0
    res = ""

    for i in l:
        if i in ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']:
            rev.append(i)
            idx.append(index)
        index += 1

    val = 0
    while (len(rev) > 0):
        l[idx[val]] = rev.pop()
        val += 1

    return res.join(l)


def reverseVowels(self, s: str) -> str:
    vowels = 'aeiouAEIOU'
    res = list(s)

    l, r = 0, len(res) - 1
    while l < r:
        while l < r and res[l] not in vowels:
            l += 1
        while l < r and res[r] not in vowels:
            r -= 1
        res[l], res[r] = res[r], res[l]
        l += 1
        r -= 1

    return ''.join(res)


def reverseVowels(self, s):
    """
    :type s: str
    :rtype: str
    """

    word = 'aeiouAEIOU'
    filter_word = [i for i in s if i in word]

    ret = list(s)
    for idx, val in enumerate(ret):
        if val in word:
            ret[idx] = filter_word.pop()

    return ''.join(ret)




