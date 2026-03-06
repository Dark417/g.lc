"""
String
0203 表示数值的字符串

题目描述
请实现一个函数用来判断字符串是否表示数值（包括整数和小数）。
例如，字符串"+100","5e2","-123","3.1416"和"-1E-16"都表示数值。
但是"12e","1a3.14","1.2.3","+-5"和"12e+4.3"都不是。


if
    s[0]

count . e


"""


# a = "ab"
# if "." or "e" in s:
#     print('1')

def isNumeric(self, s):
    # write code here
    return re.match(r"^[\+\-]?[0-9]*(\.[0-9]*)?([eE][\+\-]?[0-9]+)?$", s)


def isNumeric(self, s):
    # write code here
    pattern = re.compile(ur'(\-|\+)?\.?[0-9]+(\.[0-9]+)?([eE][\+\-]?[0-9]+)?')
    if pattern.match(s) and pattern.match(s).group() == s:
        return True
    return False



def isNumeric(self, s):
    # write code here
    # if s.endswith('e'):
    #     return False

    try:
        p = float(s)
        return True
    except:
        return False


def isNum(s):
    s = s.lower()

    if len(s) == 0: return False
    if len(s) == 1 and s not in "0123456789": return False

    if len(s) > 2:
        for i in s:
            if i not in "0123456789+=e.":
                return False

        if s[0] == 0: return False

        if s.count("e") > 1 or s.count(".") > 1:
            return False
        else:
            if s.count("+") > 1 or s.count("-") > 1:
                if s.index("+") != 0 or s.index("+") != s.index("e") + 1 or s.index("-") != 0 or s.index(
                        "-") != s.index("e") + 1:
                    return False
            else:
                if s.count(".") == 1 and s.index(".") != 1 or s.index(".") != 1:
                    return False
                if s.index("e") < s.index("."):
                    return False
                if s.index("e") == 0 or s.index(".") == 0:
                    return False

    return True


res = isNum("e100")
print(res)
