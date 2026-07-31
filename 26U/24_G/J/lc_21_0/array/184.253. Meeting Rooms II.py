"""
184.253. Meeting Rooms II
会议室 II 


给定一个会议时间安排的数组，每个会议时间都会包括开始和结束的时间 [[s1,e1],[s2,e2],...] (si < ei)，为避免会议冲突，同时要考虑充分利用会议室资源，请你计算至少需要多少间会议室，才能满足这些会议安排。

示例 1:

输入: [[0, 30],[5, 10],[15, 20]]
输出: 2
示例 2:

输入: [[7,10],[2,4]]
输出: 1

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/meeting-rooms-ii
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

"""

def minMeetingRooms(self, intervals: List[List[int]]) -> int:
    # If there is no meeting to schedule then no room needs to be allocated.
    if not intervals:
        return 0

    # The heap initialization
    free_rooms = []

    # Sort the meetings in increasing order of their start time.
    intervals.sort(key= lambda x: x[0])

    # Add the first meeting. We have to give a new room to the first meeting.
    heapq.heappush(free_rooms, intervals[0][1])

    # For all the remaining meeting rooms
    for i in intervals[1:]:

        # If the room due to free up the earliest is free, assign that room to this meeting.
        if free_rooms[0] <= i[0]:
            heapq.heappop(free_rooms)

        # If a new room is to be assigned, then also we add to the heap,
        # If an old room is allocated, then also we have to add to the heap with updated end time.
        heapq.heappush(free_rooms, i[1])

    # The size of the heap tells us the minimum rooms required for all the meetings.
    return len(free_rooms)



def minMeetingRooms(self, intervals: List[List[int]]) -> int:
    if len(intervals) == 0:
        return 0

    # 根据会议开始时间排序
    intervals.sort()
    rooms = [intervals[0][0]]   # 房间内保存最早结束时间
    for s, e in intervals:
        if rooms[0] <= s:       # 有空余房间
            heapq.heapreplace(rooms, e)
        else:                   # 没有空余房间
            heapq.heappush(rooms, e)
    return len(rooms)           # 返回房间个数




def minMeetingRooms(self, intervals: List[List[int]]) -> int:
    # 对会议的时间进行排序
    intervals.sort(key=lambda x:(x[0],x[1]))

    # 最多安排len(intervals)个房间，长度加一为了最后index(0),0的下标就是房间数
    rooms = [0]*(len(intervals)+1)
    if not intervals:
        return 0
    for start,end in intervals:
        for i in range(len(rooms)):
            if rooms[i]<=start: 
                rooms[i]=end
                break
    return rooms.index(0)



def minMeetingRooms(self, intervals: List[List[int]]) -> int:
    events = [(iv[0], 1) for iv in intervals] + [(iv[1], -1) for iv in intervals]
    events.sort()
    ans = cur = 0
    for _, e in events:
        cur += e
        ans = max(ans, cur)
    return ans



def minMeetingRooms(self, intervals: List[List[int]]) -> int:
    rooms = []  # 记录各会议室的结束时间
    meetings = sorted(intervals, key=lambda x: x[0])  # 按开始时间升序
    for meeting in meetings:
        find = False
        for index, end_time in enumerate(rooms):
            # 找到满足结束时间早于当前会议开始时间的会议室，并更新会议室的时间表
            if end_time <= meeting[0]:
                rooms[index] = meeting[1]
                find = True
                break
        # 如果没找到，则新增会议室
        if not find:
            rooms.append(meeting[1])
    return len(rooms)








































































