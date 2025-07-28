636. 函数的独占时间



def exclusiveTime(self, n: int, logs: List[str]) -> List[int]:
    res = [0] * n
    stack = []
    pret = None
    idx_pre = -1
    for i in range(len(logs)):
        idx, se, time = logs[i].split(":")
        idx = int(idx)
        time = int(time)

        if se == "start":
            if stack:
                res[stack[-1]] += time - pret

            pret = time
            stack.append(idx)

        else:
            res[stack.pop()] += time - pret + 1
            pret = time + 1
    return res

        
def exclusiveTime(self, n: int, logs: List[str]) -> List[int]:
    ans = [0] * n
    stack = []
    prev_t = None
    for s in logs:
        i, flag, t = s.split(':')
        i = int(i)
        t = int(t)
        if flag == "start":
            if len(stack) == 0:
                stack.append(i)
                prev_t = t
            else:
                ans[stack[-1]] += t - prev_t
                prev_t = t
                stack.append(i)
        if flag == "end":
            ans[stack[-1]] += t + 1 - prev_t
            prev_t = t + 1
            stack.pop(-1)
    return ans





def exclusiveTime(self, n: int, logs: List[str]) -> List[int]:
    ans = [0] * n
    st = []
    for log in logs:
        idx, tp, timestamp = log.split(':')
        idx, timestamp = int(idx), int(timestamp)
        if tp[0] == 's':
            if st:
                ans[st[-1][0]] += timestamp - st[-1][1]
                st[-1][1] = timestamp
            st.append([idx, timestamp])
        else:
            i, t = st.pop()
            ans[i] += timestamp - t + 1
            if st:
                st[-1][1] = timestamp + 1
    return ans








