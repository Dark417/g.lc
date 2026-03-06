"""
212.面试题 08.01. 三步问题



三步问题。有个小孩正在上楼梯，楼梯有n阶台阶，小孩一次可以上1阶、2阶或3阶。实现一种方法，计算小孩有
多少种上楼梯的方式。结果可能很大，你需要对结果模1000000007。

示例1:

 输入：n = 3 
 输出：4
 说明: 有四种走法
示例2:

 输入：n = 5
 输出：13
提示:

n范围在[1, 1000000]之间

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/three-steps-problem-lcci
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

"""



def waysToStep(self, n: int) -> int:
    a, b, c = 0, 0, 1
    for _ in range(n):
        a, b, c = b, c, (a+b+c)%1000000007
    return c



def waysToStep(self, n: int) -> int:
    a,b,c=4,2,1
    if n<3:
        return n
    if n==3:
        return 4
    for i in range(n-3):
        a,b,c=(a+b+c)%1000000007,a,b
    return a




def waysToStep(self, n):
    # S(n) = S(n-1)+S(n-2)+S(n-3)
    if n==0:
        return 0
    if n==1:
        return 1
    if n==2:
        return 2
    if n==3:
        return 4
    s_3,s_2,s_1 = 1,2,4
    for i in range(n-3):
        s_0 = (s_3+s_2+s_1) % 1000000007
        s_3,s_2,s_1 =s_2,s_1,s_0
    return s_0










































































