# 面试题 10.05. 稀疏数组搜索

def findString(self, words: List[str], s: str) -> int:
    left, right = 0, len(words) - 1
    while left <= right:
        mid = left + (right - left) // 2
        temp = mid  # 记录一下mid的位置，因为下面要移动mid来寻找非空串，如果查找失败需要用temp来恢复位置
        
        while words[mid] == '' and mid < right:  # 如果mid对应空串则向右寻找
            mid += 1
        if words[mid] == '':  
        # 该情况发生在mid走到了right-1的位置，如果right仍对应空，则说明temp右侧都是空，所以将右边界进行改变
            right = temp - 1
            continue
        if words[mid] == s:  # 该情况发生在mid在右移的过程中发现了非空串，则进行正常的二分查找
            return mid
        elif s < words[mid]:
            right = mid - 1
        else:
            left = mid + 1
    return -1


def findString(self, words: List[str], s: str) -> int:
        
    l, r = 0, len(words) - 1
    
    while l <= r:
        mid = l + (r - l) // 2
        tmp = mid
         
        while words[mid] == "" and mid < r:
            mid += 1
        
        if words[mid] == "":
            right = tmp - 1
            continue
        
        if words[mid] == s:
            return mid
        
        elif words[mid] < s:
            l = mid + 1
        else:
            r = mid - 1
        print(l, r)
        
    return -1


























