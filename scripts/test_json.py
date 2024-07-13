import json 

a = [1, 2, 3]
b = [4, 5, 6]
c = [7, 8, 9]

data = {
    'a': a,
    'b': b,
    'c': c
}

data_list = [data, data, data]

with open('data.json', 'w') as f:
    json.dump(data_list, f)