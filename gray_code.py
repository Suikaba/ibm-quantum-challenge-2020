def gray_code(n):
    for k in range(2 ** n):
        yield k ^ (k >> 1)

for i in gray_code(4):
    print(i)
