"""
027.537. Complex Number Multiplication
复数乘法

Given two strings representing two complex numbers.

You need to return a string representing their multiplication. 
Note i2 = -1 according to the definition.

Example 1:
Input: "1+1i", "1+1i"
Output: "0+2i"
Explanation: (1 + i) * (1 + i) = 1 + i2 + 2 * i = 2i, 
and you need convert it to the form of 0+2i.
Example 2:
Input: "1+-1i", "1+-1i"
Output: "0+-2i"
Explanation: (1 - i) * (1 - i) = 1 + i2 - 2 * i = -2i, 
and you need convert it to the form of 0+-2i.
Note:

The input strings will not have extra blank.
The input strings will be given in the form of a+bi, 
where the integer a and b will both belong to the range of [-100, 100]. And the output should be also in this form.

"""

def complexNumberMultiply(self, a: str, b: str) -> str:
        
    l1, l2 = map(lambda x: x.split("+"), (a,b))
    x = int(l1[0]) * int(l2[0]) - int(l1[1][:-1]) * int(l2[1][:-1])
    y = int(l1[0]) * int(l2[1][:-1]) + int(l2[0]) * int(l1[1][:-1])
    return str(x) + "+" + str(y) + "i"


def complexNumberMultiply(self, a: str, b: str) -> str:
    c, d = a.rstrip('i').split('+')
    e, f = b.rstrip('i').split('+')
    c, d, e, f = int(c), int(d), int(e), int(f)
    return ('{}+{}i'.format(str(c*e-d*f), str(c*f+d*e)))

    a1, a2 = map(int, a[:-1].split('+'))
    b1, b2 = map(int, b[:-1].split('+'))
    return '%d+%di' % (a1 * b1 - a2 * b2, a1 * b2 + a2 * b1)
    return "{r}+{i}i".format(r=a1*b1-a2*b2,i=a1*b2+a2*b1)

def complexNumberMultiply(self, a: str, b: str) -> str:
    ar, ai = map(int, re.split(r'[+i]', a)[:2])
    br, bi = map(int, re.split(r'[+i]', b)[:2])
    cr = str(ar*br-ai*bi)
    ci = str(ar*bi+ai*br)+'i'
    return cr+'+'+ci
















