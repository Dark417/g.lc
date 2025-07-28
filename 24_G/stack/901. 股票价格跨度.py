901. 股票价格跨度


class StockSpanner:
    def __init__(self):
        self.stk = []
        self.cur = 0

    def next(self, price: int) -> int:
        while self.stk and self.stk[-1][1] <= price:
            self.stk.pop()
        prev = -1 if not self.stk else self.stk[-1][0]
        ans = self.cur - prev
        self.stk.append([self.cur, price])
        self.cur += 1
        return ans




class StockSpanner:

    def __init__(self):
        self.stack = [(-1, inf)]
        self.idx = -1

    def next(self, price: int) -> int:
        self.idx += 1
        while price >= self.stack[-1][1]:
            self.stack.pop()
        self.stack.append((self.idx, price))
        return self.idx - self.stack[-2][0]








