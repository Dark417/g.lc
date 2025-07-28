"""
String
x008 游戏海报

题目描述
小明有26种游戏海报，用小写字母"a"到"z"表示。
小明会把游戏海报装订成册（可能有重复的海报），册子可以用一个字符串来表示，
每个字符就表示对应的海报，例如abcdea。小明现在想做一些“特别版”，然后卖掉。
特别版就是会从所有海报（26种）中随机选一张，加入到册子的任意一个位置。
那现在小明手里已经有一种海报册子，再插入一张新的海报后，他一共可以组成多少不同的海报册子呢？
输入描述:
海报册子的字符串表示，1 <= 字符串长度<= 20
输出描述:
一个整数，表示可以组成的不同的海报册子种类数
示例1
输入
复制
a
输出
复制
51
说明
我们可以组成 'ab','ac',...,'az','ba','ca',...,'za' 还有 'aa', 一共 51 种不同的海报册子。


"""





s = raw_input()
slen = len(s)

rs = (slen + 1) * 26 - slen

print (rs)


import sys
for line in sys.stdin:
    msize = len(line)-1
    print((msize+1)*26-msize)


import sys
import bisect
from itertools import permutations
import operator

try:
    while True:
        str1 = raw_input()
        length = len(str1)
        res = (26 - length) * (length + 1) + length * length
        print(res)



import sys

if __name__ == "__main__":
    # sys.stdin = open("input.txt", "r")
    s = input().strip()
    ans = (len(s) + 1) * 26 - len(s)
    print(ans)





# C
int main(){
    char a[21];
    scanf("%s",a);
    int l=0;
    while(a[l]!='\0')
    {
        ++l;
    }
    printf("%d",26*(l+1)-l);
    return 0;
}


# C2
char str[30];
int main()
{
    gets(str);
    int len=strlen(str);
    int rs=26*(len+1)-len;
    printf("%d\n",rs);
    return 0;
}











