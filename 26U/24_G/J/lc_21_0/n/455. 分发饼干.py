# 455. 分发饼干



def findContentChildren(self, g: List[int], s: List[int]) -> int:
    
    g.sort()
    s.sort()
    
    gl = len(g)
    sl = len(s)
    
    gi = si = x = 0

    while gi < gl and si < sl:
        if g[gi] <= s[si]:
            x += 1
            gi += 1
            si += 1
        else:
            si += 1
    
    return x



def findContentChildren(self, g: List[int], s: List[int]) -> int:
    g.sort()
    s.sort()
    
    gl = len(g)
    sl = len(s)
    
    gi = gl-1
    si = sl-1
    x = 0

    while gi>=0 and si>=0:
        if g[gi] <= s[si]:
            x += 1
            gi -= 1
            si -= 1
        else:
            gi -= 1
    
    return x


def findContentChildren(self, g: List[int], s: List[int]) -> int:
    g.sort()
    s.sort()
    n, m = len(g), len(s)
    i = j = count = 0

    while i < n and j < m:
        while j < m and g[i] > s[j]:
            j += 1
        if j < m:
            count += 1
        i += 1
        j += 1
    
    return count






