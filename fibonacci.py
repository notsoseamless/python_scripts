


def fib(n):    # write Fibonacci series up to n
	"""Print a Fibonacci series up to n."""
	result = []
	a, b = 0,1
	while a < n:
		result.append(a)
		a, b = b, a+b
	return result


f = fib(1000000)

print(f)
