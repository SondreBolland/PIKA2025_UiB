def add(a, b, c):
	max = 0
	if (a < b) and (a < c):
		max = b + c
		return max
	elif (b < a) and (b < c):
		max = a + c
		return max
	else:
		max = a + b
		return max
	print(max)

add(8, 5, 12)