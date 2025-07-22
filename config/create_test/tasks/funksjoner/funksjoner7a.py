def f(x):
    x = x + 2
    return x - 1

def g(x):
    x = f(x) + 3
    return x

print(f(2) + f(3))