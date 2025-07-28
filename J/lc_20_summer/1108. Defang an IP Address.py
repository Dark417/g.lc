"""
1108. Defanging an IP Address

Input: address = "255.100.50.0"
Output: "255[.]100[.]50[.]0"

Given a valid (IPv4) IP address, return a defanged version of that IP address.

A defanged IP address replaces every period "." with "[.]".
"""

input = "255.100.50.0"


#discussion
def defangIPaddr(self, address: str) -> str:
    return address.replace('.', '[.]')


def defangIPaddr(self, address: str) -> str:
    return '[.]'.join(address.split('.'))


def defangIPaddr(self, address: str) -> str:
    return re.sub('\.', '[.]', address)


>>> timeit.timeit(lambda: '1.1.1.1'.replace('.', '[.]'), number=1000000)
0.2977291930001229
>>> timeit.timeit(lambda: '[.]'.join('1.1.1.1'.split('.')), number=1000000)
0.35931704599988734


# my
def defang_dic(address):
    result = ''
    dic = {}
    comma = 0
    for i in range(4):
        dic[i] = ''

    for i in address:
        if i == '.':
            result = result + dic[comma] + '[.]'
            comma += 1
        else:
            dic[comma] = dic[comma] + i

    result = result + dic[comma]
    return result

print(defang_dic(input))


def defang_str_iterate(input):
    result = ''
    comma = 0
    list = [''] * 4

    for i in input:
        if i == '.':
            result = result + list[comma] + '[.]'
            comma += 1
            # print('comma ', comma)
            # print('result ', result)
        else:
            list[comma] = list[comma] + i
            # print('listcomma ', list[comma])
    result = result + list[comma]
    return result


def defang_str_split(input):
    result = ''
    splitted = input.split(".")

    for i in splitted[:-1]:
        result = result + i + "[.]"
    result = result + splitted[-1]
    return result

