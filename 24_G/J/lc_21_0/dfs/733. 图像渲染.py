# 733. 图像渲染

def floodFill(self, image: List[List[int]], sr: int, sc: int, newColor: int) -> List[List[int]]:
	def dfs(sr, sc, new, old):
		if sr < 0 or sc < 0 or sr >= len(image) or sc >= len(image[0]) 
			or image[sr][sc] != old or new == old:
			return
		image[sr][sc] = new
		dfs(sr - 1, sc, new, old)
		dfs(sr + 1, sc, new, old)
		dfs(sr, sc - 1, new, old)
		dfs(sr, sc + 1, new, old)
	dfs(sr, sc, newColor, image[sr][sc])
	return image


def floodFill(self, image: List[List[int]], sr: int, sc: int, newColor: int) -> List[List[int]]:
    n, m = len(image), len(image[0])
    currColor = image[sr][sc]

    def dfs(x: int, y: int):
        if image[x][y] == currColor:
            image[x][y] = newColor
            for mx, my in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                if 0 <= mx < n and 0 <= my < m and image[mx][my] == currColor:
                    dfs(mx, my)

    if currColor != newColor:
        dfs(sr, sc)
    return image



def floodFill(self, image: List[List[int]], sr: int, sc: int, newColor: int) -> List[List[int]]:
    currColor = image[sr][sc]
    if currColor == newColor:
        return image
    
    n, m = len(image), len(image[0])
    que = collections.deque([(sr, sc)])
    image[sr][sc] = newColor
    while que:
        x, y = que.popleft()
        for mx, my in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if 0 <= mx < n and 0 <= my < m and image[mx][my] == currColor:
                que.append((mx, my))
                image[mx][my] = newColor
    
    return image



def floodFill(self, image: List[List[int]], sr: int, sc: int, newColor: int) -> List[List[int]]:
    if newColor == image[sr][sc]:
    	return image
    que, old,  = [(sr, sc)], image[sr][sc]
    while que:
        point = que.pop()
        image[point[0]][point[1]] = newColor
        for new_i, new_j in zip((point[0], point[0], point[0] + 1, point[0] - 1), (point[1] + 1, point[1] - 1, point[1], point[1])): 
            if 0 <= new_i < len(image) and 0 <= new_j < len(image[0]) and image[new_i][new_j] == old:  
                que.insert(0,(new_i,new_j))
    return image


























