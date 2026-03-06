"""
239.925. Long Pressed Name
长按键入


Your friend is typing his name into a keyboard.  Sometimes, when typing a character c, the key might get long pressed, and the character will be typed 1 or more times.

You examine the typed characters of the keyboard.  Return True if it is possible that it was your friends name, with some characters (possibly none) being long pressed.

 

Example 1:

Input: name = "alex", typed = "aaleex"
Output: true
Explanation: 'a' and 'e' in 'alex' were long pressed.
Example 2:

Input: name = "saeed", typed = "ssaaedd"
Output: false
Explanation: 'e' must have been pressed twice, but it wasn't in the typed output.
Example 3:

Input: name = "leelee", typed = "lleeelee"
Output: true
Example 4:

Input: name = "laiden", typed = "laiden"
Output: true
Explanation: It's not necessary to long press any character.
 

Constraints:

1 <= name.length <= 1000
1 <= typed.length <= 1000
The characters of name and typed are lowercase letters.

"""


def isLongPressedName(self, name, typed):
    i = 0
    for j in range(len(typed)):
        if i < len(name) and name[i] == typed[j]:
            i += 1
        elif j == 0 or typed[j] != typed[j - 1]:
            return False
    return i == len(name)


    return all(ch1 == ch2 and len(list(g1)) <= len(list(g2)) 
    	for ((ch1, g1), (ch2, g2)) in zip_longest(groupby(name), groupby(typed), fillvalue=(None, None)))




def isLongPressedName(self, name, typed):
    g1 = [(k, len(list(grp))) for k, grp in itertools.groupby(name)]
    g2 = [(k, len(list(grp))) for k, grp in itertools.groupby(typed)]
    if len(g1) != len(g2):
        return False

    return all(k1 == k2 and v1 <= v2
               for (k1,v1), (k2,v2) in zip(g1, g2))





def isLongPressedName(self, name: str, typed: str) -> bool:
    # two pointers to the "name" and "typed" string respectively
    np, tp = 0, 0

    # advance two pointers, until we exhaust one of the strings
    while np < len(name) and tp < len(typed):
        if name[np] == typed[tp]:
            np += 1
            tp += 1
        elif tp >= 1 and typed[tp] == typed[tp-1]:
            tp += 1
        else:
            return False

    # if there is still some characters left *unmatched* in the origin string,
    #   then we don't have a match.
    # e.g.  name = "abc"  typed = "aabb"
    if np != len(name):
        return False
    else:
        # In the case that there are some redundant characters left in typed
        # we could still have a match.
        # e.g.  name = "abc"  typed = "abccccc"
        while tp < len(typed):
            if typed[tp] != typed[tp-1]:
                return False
            tp += 1

    # both strings have been consumed
    return True





def isLongPressedName(self, name, typed):
    i, j = 0, 0
    while i < len(name) and j < len(typed):
        if name[i] == typed[j]:
            i += 1
            j += 1
        else:
            j += 1
    if i == len(name):
        return True
    return False



 def isLongPressedName(self, name: str, typed: str) -> bool:
    la, lt = len(name), len(typed)
    i = j = 0
    while i < la and j < lt:
        if name[i] == typed[j]: i, j = i + 1, j + 1
        elif i > 0 and typed[j] == name[i-1]: j += 1
        else: return False
    return i == la and all(typed[i] == name[-1] for i in range(j, lt))






















































































