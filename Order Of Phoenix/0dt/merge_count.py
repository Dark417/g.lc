#homework from...
#

merge_count(B, C, n1, n2)
	count = 0
	A = []
	i = 1, j = 1
	while i <= n1 or j <= n2
		if j > n2 or (i <= n1 and B[i] <= C[j])
			A.append(B[i])
			i = i + 1
		elif
			if B[i] > 2*C[j]
				count = count + 1
			A.append(C[j])
			j = j + 1
	return (A, count)

sort_count(A, n)
	if n = 1 return (A, 0)
	else
		(B, m1) = sort_count(A[1...floor(n/2)], floor(n/2))
		(C, m2) = sort_count(A[floor(n/2)+1...n], ceiling(n/2))
		(A, m3) = sort_count(B, C, floor(n/2), ceiling(n/2))
		return (A, m1 + m2 + m3)




cross_max(B, C, n1, n2, max_b, max_c)
	A = []
	i = n1, j = n2
	max_cross = 0
	while i <= n1 or j <= n2
		if i < 0 or (j >= 0 and C[j] >= B[i])
			A.append(C[j])
			max_cross = max(max_cross, C[j] - B[i])
			i = i - 1
		else
			A.append[B[i]]
			j = j - 1
	max_out = max(max_b, max_c, max_cross)
	return(A, max_out)

merge_sort_max(A, n)
	if n = 1 return (A, 0)
	else
		(B, max1) = cross_max(A[1...floor(n/2)], floor(n/2))
		(C, max2) = cross_max(A[floor(n/2)+1...n], ceiling(n/2))
		(A, max_result) = cross_max(B, C, floor(n/2), ceiling(n/2), max1, max2)
		return (A, max_result)