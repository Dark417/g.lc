# 290. 单词规律

return False if len(tmp := s.split()) != len(pattern) else len(set(zip(pattern, tmp))) == len(set(tmp)) == len(set(pattern))


def wordPattern(self, pattern, str):
    s = pattern
    t = str.split()
    return map(s.find, s) == map(t.index, t)


def wordPattern(self, pattern, str):
    f = lambda s: map({}.setdefault, s, range(len(s)))
    return f(pattern) == f(str.split())


def wordPattern(self, pattern, str):
    s = pattern
    t = str.split()
    return len(set(zip(s, t))) == len(set(s)) == len(set(t)) and len(s) == len(t)



def f(sequence):
    first_occurrence = {}
    normalized = []
    for i, item in enumerate(sequence):
        if item not in first_occurrence:
            first_occurrence[item] = i
        normalized.append(first_occurrence[item])
    return normalized


    
def wordPattern(self, pattern: str, s: str) -> bool:
    map_index = {}
    words = s.split()
    
    if len(pattern) != len(words):
        return False
    
    for i in range(len(words)):
        c = pattern[i]
        w = words[i]

        char_key = 'char_{}'.format(c)
        char_word = 'word_{}'.format(w)
        
        if char_key not in map_index:
            map_index[char_key] = i
        
        if char_word not in map_index:
            map_index[char_word] = i 
        
        if map_index[char_key] != map_index[char_word]:
            return False
    
    return True



def wordPattern(self, pattern: str, s: str) -> bool:
    words = s.split()
    if len(pattern) != len(words):
        return False
    dc = {}
    st = set()
    for i in range(len(pattern)):
        if pattern[i] not in dc:
            if words[i] not in st:
                dc[pattern[i]] = words[i]
                st.add(words[i])
            else:
                return False
        else:
            if words[i] != dc[pattern[i]]:
                return False
    return True



def wordPattern(self, pattern: str, s: str) -> bool:
    word2ch = dict()
    ch2word = dict()
    words = s.split()
    if len(pattern) != len(words):
        return False
    
    for ch, word in zip(pattern, words):
        if (word in word2ch and word2ch[word] != ch) or (ch in ch2word and ch2word[ch] != word):
            return False
        word2ch[word] = ch
        ch2word[ch] = word

    return True

































