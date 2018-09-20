e = {};n = {}
for item in ['True', 'False', 'Mixed']:
    e[item] = {}
    n[item] = {}
    for d_type in ['time_depth', 'user_depth']:
        e[item][d_type] = {}
        n[item][d_type] = {}

        for i in range(1,20):
            e[item][d_type][i] = []
            n[item][d_type][i] = []

#print(e)
#print(n)
v = 'True'
e[v]['time_depth'][1].append(1)
e[v]['time_depth'][1].append(3)
e[v]['time_depth'][1].append(2)
e[v]['time_depth'][1].append(1)
print(e[v]['time_depth'][1])
