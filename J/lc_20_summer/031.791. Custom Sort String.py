"""
031.791. Custom Sort String
自定义字符串排序

S and T are strings composed of lowercase letters. In S, 
no letter occurs more than once.

S was sorted in some custom order previously. 
We want to permute the characters of T so that they match the order that 
S was sorted. More specifically, if x occurs before y in S, 
then x should occur before y in the returned string.

Return any permutation of T (as a string) that satisfies this property.

Example :
Input: 
S = "cba"
T = "abcd"
Output: "cbad"
Explanation: 
"a", "b", "c" appear in S, so the order of "a", "b", "c" should be "c", "b", and "a". 
Since "d" does not appear in S, it can be at any position in T. "dcba", "cdba", "cbda" are also valid outputs.
 

Note:

S has length at most 26, and no character is repeated in S.
T has length at most 200.
S and T consist of lowercase letters only.

"""

def customSortString(self, S: str, T: str) -> str:
    ret = ""
    for i in S:
        if i in T:
            ret += i
    for i in set(T):
        if i not in ret:
                ret += T.count(i)*i
        else:
            ret += i*(T.count(i)-1)
    return ret

    return "".join(sorted(T, key = S.find))


def customSortString(self, S: str, T: str) -> str:
	l = []
    for i in S:
            l.append(i*T.count(i))
    for i in T:
        if i not in S:
            l.append(i)
    return ''.join(l)


def customSortString(self, S, T):
    # count[char] will be the number of occurrences of
    # 'char' in T.
    count = collections.Counter(T)
    ans = []

    # Write all characters that occur in S, in the order of S.
    for c in S:
        ans.append(c * count[c])
        # Set count[c] = 0 to denote that we do not need
        # to write 'c' to our answer anymore.
        count[c] = 0

    # Write all remaining characters that don't occur in S.
    # That information is specified by 'count'.
    for c in count:
        ans.append(c * count[c])

    return "".join(ans)



























































