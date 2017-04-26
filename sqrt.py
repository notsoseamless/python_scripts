'''
find square root using Newton's method

converted from a scala snipit

JRO July 2015

'''

def sqrt(x):
    def sqrtIter(guess):
        if isGoodEnough(guess):
            return guess
        else:
            return sqrtIter(improve(guess))

    def improve(guess):
        return (guess + x / guess) / 2

    def isGoodEnough(guess):
        return abs((guess * guess) - x) < 0.001

    return sqrtIter(1.0)

print sqrt(2.0)
print sqrt(3.0)
print sqrt(4.0)



