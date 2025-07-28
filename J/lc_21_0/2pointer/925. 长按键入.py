# 925. 长按键入

def isLongPressedName(self, name, typed):
    i = 0
    for j in range(len(typed)):
        if i < len(name) and name[i] == typed[j]:
            i += 1
        elif j == 0 or typed[j] != typed[j - 1]:
            return False
    return i == len(name)


def isLongPressedName(self, name: str, typed: str) -> bool:
    i = j = 0
    while j < len(typed):
        if i < len(name) and typed[j] == name[i]:
            i += 1
            j += 1
        elif j > 0 and typed[j] == typed[j - 1]:
            j += 1
        else:
            return False

    return i == len(name) 



def isLongPressedName(self, name: str, typed: str) -> bool:
    i = 0
    name += "1"
    for s in typed:
        if s == name[i]:
            i += 1
        elif s != name[i-1]:
            return False
    return i == len(name) - 1
















