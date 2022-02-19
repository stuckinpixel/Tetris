data = [
    [1, 1, 1],
    [0, 1, 0]
]

data = [
        [1, 1, 1],
        [1, 0, 0],
        [1, 0, 0]
]

result = []
for i in range(len(data[0])-1, -1, -1):
    new_row = []
    for j in range(len(data)):
        new_row.append(data[j][i])
    result.append(new_row)

print (result)
















