"""
050.824. Goat Latin
山羊拉丁文

A sentence S is given, composed of words separated by spaces. Each word consists of lowercase and uppercase letters only.

We would like to convert the sentence to "Goat Latin" (a made-up language similar to Pig Latin.)

The rules of Goat Latin are as follows:

If a word begins with a vowel (a, e, i, o, or u), append "ma" to the end of the word.
For example, the word 'apple' becomes 'applema'.
 
If a word begins with a consonant (i.e. not a vowel), remove the first letter and append it to the end, then add "ma".
For example, the word "goat" becomes "oatgma".
 
Add one letter 'a' to the end of each word per its word index in the sentence, starting with 1.
For example, the first word gets "a" added to the end, the second word gets "aa" added to the end and so on.
Return the final sentence representing the conversion from S to Goat Latin. 

Example 1:

Input: "I speak Goat Latin"
Output: "Imaa peaksmaaa oatGmaaaa atinLmaaaaa"
Example 2:

Input: "The quick brown fox jumped over the lazy dog"
Output: "heTmaa uickqmaaa rownbmaaaa oxfmaaaaa umpedjmaaaaaa overmaaaaaaa hetmaaaaaaaa azylmaaaaaaaaa ogdmaaaaaaaaaa"
 

Notes:

S contains only uppercase, lowercase and spaces. Exactly one space between each word.
1 <= S.length <= 150.


"""

#regexp
if re.match(r'(?i)^[aeiou]', w):



def toGoatLatin(self, S: str) -> str:
    l = S.split()
    ret = []
    for i in l:
        if i[0] in "aeiouAEIOU":
            ret.append(i + "ma")
        else:
            ret.append(i[1:] + i[0] + "ma")
    for i in range(len(ret)):
        ret[i] += "a"*(i+1)
    return " ".join(ret)


def toGoatLatin(self, S):
    def convert(word):
        if word[0] not in 'aeiouAEIOU':
            word = word[1:] + word[:1]
        return word + 'ma'

    return " ".join(convert(word) + 'a' * i
                    for i, word in enumerate(S.split(), 1))

def toGoatLatin(self, S):
	vowel = set('aeiouAEIOU')
    def latin(w, i):
        if w[0] not in vowel:
            w = w[1:] + w[0]
        return w + 'ma' + 'a' * (i + 1)
    return ' '.join(latin(w, i) for i, w in enumerate(S.split()))

    return ' '.join((w if w[0].lower() in 'aeiou' else w[1:] + w[0]) + 'ma' + 'a' * (i + 1) for i, w in enumerate(S.split()))
    return " ".join([ (word[1:] + word[0] if word[0].lower() not in 'aeiou' else word)  + 'ma' + 'a'* (i + 1) for i, word in enumerate(S.split(' '))])


def toGoatLatin(self, S):
    s, vowels = S.split(), {"a", "e", "i", "o", "u"} 
    return " ".join([(s[i][0].lower() in vowels and s[i] or s[i][1:] + s[i][0]) + "m" + "a" * (i + 2) for i in range(len(s))])

def toGoatLatin(self, S):
        s, vowels = S.split(), {"a", "e", "i", "o", "u"}
        for i, char in enumerate(s):
            s[i] = char[1:] + char[0] + "ma" + "a" * (i + 1) if char[0].lower() not in vowels else char + "ma" + "a" * (i + 1)  
        return " ".join(s)



def toGoatLatin(self, S):
	words = S.split()
    vowels = 'AEIOUaeiou'
    def transform(stuff):
        idx, word = stuff
        if word[0] in vowels:
            word += 'ma'
        else:
            word = word[1:] + word[0] + 'ma'
        word += 'a'*(idx+1)    
        return word
    return " ".join(list(map(transform, enumerate(words))))




def toGoatLatin(self, S: str) -> str:
    index=1
    beginning=1
    consonant=''
    vowels=('a','e','i','o','u','A','E','I','O','U')
    ans=''
    for i in S:
        if i==' ':
            ans+=consonant+'a'*index+' '
            index+=1
            beginning=1
        else:
            if beginning==1:
                beginning=0
                if i in vowels:ans+=i;consonant='ma'
                else:consonant=i+'ma'
            else:
                ans+=i
    return ans+consonant+'a'*index


def toGoatLatin(self, S: str) -> str:
        S=[word for word in S.split()]
        res=''
        for i,v in enumerate(S):
            if v[0] in 'aeiouAEIOU':
                res=res+v+'ma'
            else:
                res= res+v[1:]+v[:1]+'ma'
            res=res+'a'*(i+1)
            if i<len(S)-1:
                res+=" "
        return res











































