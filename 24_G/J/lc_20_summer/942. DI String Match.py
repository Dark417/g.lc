"""
942. DI String Match

Given a string S that only contains "I" (increase) or "D" (decrease), let N = S.length.
Return any permutation A of [0, 1, ..., N] such that for all i = 0, ..., N-1:

If S[i] == "I", then A[i] < A[i+1]
If S[i] == "D", then A[i] > A[i+1]

Example 1:
Input: "IDID"
Output: [0,4,1,3,2]
Example 2:

Input: "III"
Output: [0,1,2,3]
Example 3:

Input: "DDI"
Output: [3,2,0,1]

Note:
1 <= S.length <= 10000
S only contains characters "I" or "D".

psd
track relative
elevate!

"""
input = "DDIDII"
# DDIIIDID

#2
def diStringMatch(self, S):
    i = 0
    j = len(S)
    ans = []

    for x in S:
        if x == 'I':
            ans.append(i)
            i += 1
        else:
            ans.append(j)
            j -= 1
    ans.append(j)  # latest element
    # ans.append(j if S[-1] == 'D' else i)
    return ans

#3
def diStringMatch(self, S):
    l = []
    a = 0
    b = len(S)
    S = S+S[len(S)-1]
    for i in S:
        if i=='I':
            l.append(a)
            a+=1
        else:
            l.append(b)
            b=b-1
    return(l)

#x
def di_strx(input):
    left = right = 0
    res = [0]
    for i in S:
        if i == "I":
            right += 1
            res.append(right)
        else:
            left -= 1
            res.append(left)
    return [i - left for i in res]


def di_str(input):
    res = [0]
    left = right = 0
    for i in input:
        if i == "I":
            left += 1
            res.append(i)
        else:
            right -= 1
            res.append(i)

    return result(i - left for i in res)

def di_str_rl(input):
    res = [0]
    left = 1; right = len(input)

    for i in input:
        if i == "I":
            res.append(right)
            right -= 1
        else:
            res.append(left)
            left += 1
    return res

result = di_str(input)
print(result)























