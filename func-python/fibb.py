def fibonacci(): 
    c = 0
    n = 1
    while True:
        yield c
        c, n = n, c + n

for i in fibonacci():
    print(i)
    if i > 100:
        break