# 744. 寻找比目标字母大的最小字母



def nextGreatestLetter(self, letters, target):
    seen = set(letters)
    for i in xrange(1, 26):
        cand = chr((ord(target) - ord('a') + i) % 26 + ord('a'))
        if cand in seen:
            return cand


def nextGreatestLetter(self, letters, target):
        for c in letters:
            if c > target:
                return c
        return letters[0]

def nextGreatestLetter(self, letters, target):
        index = bisect.bisect(letters, target)
        return letters[index % len(letters)]





def nextGreatestLetter(self, letters: List[str], target: str) -> str:
    length = len(letters)
    left = 0
    right = length-1
    while(left<=right):
        mid = (left+right)//2
        if letters[mid]>target:
            right = mid-1
        else:
            left = mid+1
    if left == length:
        return letters[0]
    else:
        return letters[left]



























