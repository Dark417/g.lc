"""
893. Groups of Special-Equivalent Strings
特殊等价字符串组

You are given an array A of strings.

A move onto S consists of swapping any two even indexed characters of S, 
or any two odd indexed characters of S.

Two strings S and T are special-equivalent if after any number of moves onto S, 
S == T.

For example, S = "zzxy" and T = "xyzz" are special-equivalent because 
we may make the moves "zzxy" -> "xzzy" -> "xyzz" that swap S[0] and S[2], 
then S[1] and S[3].

Now, a group of special-equivalent strings from A is a non-empty subset of A 
such that:

Every pair of strings in the group are special equivalent, and;
The group is the largest size possible (ie., there isn't a string S not in the 
group such that S is special equivalent to every string in the group)
Return the number of groups of special-equivalent strings from A.

 
Example 1:

Input: ["abcd","cdab","cbad","xyzz","zzxy","zzyx"]
Output: 3
Explanation: 
One group is ["abcd", "cdab", "cbad"], 
since they are all pairwise special equivalent, 
and none of the other strings are all pairwise special equivalent to these.

The other two groups are ["xyzz", "zzxy"] and ["zzyx"].  
Note that in particular, "zzxy" is not special equivalent to "zzyx".
Example 2:

Input: ["abc","acb","bac","bca","cab","cba"]
Output: 3
 

Note:

1 <= A.length <= 1000
1 <= A[i].length <= 20
All A[i] have the same length.
All A[i] consist of only lowercase letters.
"""

def numSpecialEquivGroups(self, A: List[str]) -> int:
    return len({(''.join(sorted(str[::2]) +sorted(str[1::2]))) for str in A})

    return len({''.join(sorted(a[:: 2]) + sorted(a[1:: 2])) for a in A})
    return len({tuple(sorted(a[:: 2]) + sorted(a[1:: 2])) for a in A})

    return len(set("".join(sorted(s[0::2])) + "".join(sorted(s[1::2])) for s in A))
    return len({("".join(sorted(s[0::2])), "".join(sorted(s[1::2]))) for s in A})
    return len({''.join(sorted(s[::2]) + sorted(s[1::2])) for s in A})
    return len({tuple(sorted(s[0::2]) + sorted(s[1::2])) for s in A})



def numSpecialEquivGroups(self, A):
    def count(A):
        ans = [0] * 52
        for i, letter in enumerate(A):
            ans[ord(letter) - ord('a') + 26 * (i%2)] += 1
        return tuple(ans)

    return len({count(word) for word in A})


def numSpecialEquivGroups(self, A: List[str]) -> int:
    str_dict = {}
    for s in A:
        key, item = [0] * 26, [0] * 26
        for i in range(len(s)):
            key[ord(s[i]) - ord('a')] += 1
            item[ord(s[i]) - ord('a')] += 1 if i & 1 else -1
        key, item = tuple(key), tuple(item)
        if key in str_dict.keys():
            str_dict[key].add(item)
        else:
            str_dict[key] = {item}
    return sum([len(value) for value in str_dict.values()])



def numSpecialEquivGroups(self, A: List[str]) -> int:
    res=set()
    for i in A:
        tmp="".join(sorted(i[1::2])+sorted(i[::2]))
        res.add(tmp)
    return len(res)


def numSpecialEquivGroups(self, A: List[str]) -> int:
    res = set()
    for sub in A:
        sub = ''.join(sorted(sub[::2]) + sorted(sub[1::2]))
        res.add(sub)
    return len(res)


def numSpecialEquivGroups(self, A: List[str]) -> int:
    res = set()
    for s in A:
        sort_odd_even = ''.join(sorted(s[1::2]) + sorted(s[::2]))
        res.add(sort_odd_even)
    return len(res)






