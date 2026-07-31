"""
dynamic programming
Fibonacci Sequence
大家都知道斐波那契数列，现在要求输入一个整数n，
请你输出斐波那契数列的第n项（从0开始，第0项为0）。
n<=39

"""


def Fibonacci(self, n):
    # write code here
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def Fibonacci(n):
    f = 0
    g = 1
    while n != 0:
        g += f
        f = g - f
        n -= 1
    return f


def Fibonacci(self, n):
    # write code here
    res = [0, 1, 1, 2]
    while len(res) <= n:
        res.append(res[-1] + res[-2])
    return res[n]


def fibonacci_sequence(n):
    f = [0] * 100
    f[1] = 1
    f[2] = 1

    i = 3
    while i <= n:
        f[i] = f[i - 1] + f[i - 2]
        i += 1
    return f[n]


def Fibonacci(self, n):
    # write code here
    if n == 0:
        return 0
    if n == 1:
        return 1
    if n == 2:
        return 1
    if n >= 3:
        s = [] * n
        s.append(1)
        s.append(1)
        for i in xrange(2, n):
            s.append(s[i - 1] + s[i - 2])
        return s[n - 1]

def Fibonacci(self, n):
    a = [0, 1, 1]
    if n < 3:
        return a[n]
    for i in range(3, n + 1):
        a.append(a[i - 1] + a[i - 2])
    return a[n]

def Fibonacci(self, n=39):
    # write code here
    f0, f1 = 0, 1
    if n == 0:
        return 0
    elif n == 1:
        return 1
    for i in xrange(2, n + 1):
        a = f0 + f1
        f0 = f1
        f1 = a
    return a





public int Fibonacci(int n) {
        int a=1,b=1,c=0;
        if(n<0){
            return 0;
        }else if(n==1||n==2){
            return 1;
        }else{
            for (int i=3;i<=n;i++){
                c=a+b;
                b=a;
                a=c;
            }
            return c;
        }
    }

public int Fibonacci(int n) {
    if(n==0) return 0;
        if(n==1|| n==2) return 1;
        int arr[] = new int[n];
        arr[0] = arr[1] = 1;
        for (int i = 2; i < n; i++) {
            arr[i] = arr[i - 1] + arr[i - 2];
        }
        return arr[n - 1];
    }

public int Fibonacci(int n) {
        if(n <= 0)return 0;
        if(n == 1)return 1;
        int a = 0, b = 1, c = 0;
        for(int i = 1; i < n; i++){
            c = a + b;
            a = b;
            b = c;
        }
        return c;
}


