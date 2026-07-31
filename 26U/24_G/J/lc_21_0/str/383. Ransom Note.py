"""
049.383. Ransom Note
赎金信

Given an arbitrary ransom note string and another string containing letters from all the magazines, write a function that will return true if the ransom note can be constructed from the magazines ; otherwise, it will return false.

Each letter in the magazine string can only be used once in your ransom note.

 

Example 1:

Input: ransomNote = "a", magazine = "b"
Output: false
Example 2:

Input: ransomNote = "aa", magazine = "ab"
Output: false
Example 3:

Input: ransomNote = "aa", magazine = "aab"
Output: true
 

Constraints:

You may assume that both strings contain only lowercase letters.





"""
def canConstruct(self, ransomNote: str, magazine: str) -> bool:

	return not collections.Counter(ransomNote) - collections.Counter(magazine)
	return not len(Counter(ransomNote) - Counter(magazine))
	return (Counter(ransomNote) - Counter(magazine)) == {}

	return all(ransomNote.count(c)<=magazine.count(c) for c in string.ascii_lowercase)
	return all(ransomNote.count(x) <= magazine.count(x) for x in set(ransomNote) )
	return all(ransomNote.count(c)<=magazine.count(c) for c in ransomNote)
	


def canConstruct(self, ransomNote: str, magazine: str) -> bool:
	ran = collections.Counter(ransomNote)
    mag = collections.Counter(magazine)
    return ran & mag == ran


def canConstruct(self, ransomNote: str, magazine: str) -> bool:
    hash_table_m = collections.Counter(magazine)
    hash_table_r = collections.Counter(ransomNote)
    return not hash_table_r - hash_table_m



def canConstruct(self, ransomNote: str, magazine: str) -> bool:
    from collections import Counter
    rdic = Counter(ransomNote)
    mag = Counter(magazine)
    for c in rdic:
        if rdic[c] > mag[c]:
            return False
    return True

    # set
	for i in set(ransomNote):
        if ransomNote.count(i) > magazine.count(i):
            return False
    return True

    # chr
    count = [0] * 26
        for i in range(26):
            x = chr(97 + i)
            count[i] = magazine.count(x)
            count[i] -= ransomNote.count(x)
            
            if count[i] < 0:
                return False
        return True

def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        from collections import Counter
        dict1 = dict(Counter(ransomNote))
        dict2 = dict(Counter(magazine))
        for i in dict1 :
            if not i in dict2 :
                return False
            else:
                if dict1[i] > dict2[i] :
                    return False
        return True


def canConstruct(self, ransomNote: str, magazine: str) -> bool:
    for c in ransomNote:
        if ransomNote.count(c) > magazine.count(c):
            return False
    return True


def canConstruct(self, ransomNote: str, magazine: str) -> bool:
    for i in ransomNote:
        if i in magazine:
            magazine = magazine.replace(i,"",1)
        else: return False
    
    return True

def canConstruct(self, ransomNote: str, magazine: str) -> bool:
	for char in ransomNote:
	        if char in magazine:
	            magazine = magazine.replace(char, '', 1)
	        else:
	            return False
	    return True

def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        numRansomNote = len(ransomNote)
        for letter in magazine:
            if (letter in ransomNote and numRansomNote > 0):
                ransomNote = ransomNote.replace(letter, "",1)
                numRansomNote -= 1        
        return numRansomNote == 0


def canConstruct(self, ransomNote, magazine):
    c1, c2 = collections.Counter(ransomNote), collections.Counter(magazine)
    return all(k in c2 and c2[k]>=c1[k] for k in c1)


def canConstruct(self, ransomNote, magazine):
    s, i = sorted(ransomNote), 0
    for c in sorted(magazine):
        i += i<len(s) and s[i]==c
    return i==len(s)


def canConstruct(self, ransomNote, magazine):
    s1, s2, i = sorted(ransomNote), sorted(magazine), 0
    for c in s2:
        if i==len(s1) or c>s1[i]:
            break
        if c==s1[i]:
            i += 1
    return i==len(s1)


def canConstruct(self, ransomNote: str, magazine: str) -> bool:
	a = [0]*26
	for note in magazine:
	a[ord(note) - ord('a')] += 1

	for note in ransomNote:
	index = ord(note) - ord('a')
	a[index] -= 1
	if a[index] < 0:
	  return False

	return True


for ch in ransomNote:
        index = -1
        try:
            index = magazine.index(ch)
        except ValueError:
            index = -1
        if index == -1:
            return False
        magazine = magazine[:index] + magazine[index+1:]
    return True

   


   


   


   


   


   


   


   


