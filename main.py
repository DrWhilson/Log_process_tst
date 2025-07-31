import json

data = []
with open('example1.log', 'r', encoding='utf-8') as file:
    for line in file:
        data.append(json.loads(line.strip()))

for i in range(len(data)):
    print(data[i])
