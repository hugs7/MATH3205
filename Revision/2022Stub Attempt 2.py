from gurobipy import *
import random

# Range of possible sizes - 21 to 50
Size = range(21, 51)

Capacity = 120

# At least one item of each Size
Count = {s: 1 for s in Size}

nItems = 70

# DO NOT CHANGE THIS SEED!
random.seed(7)

# Other items allocated randomly
for i in range(nItems-len(Size)):
    Count[random.choice(Size)] += 1

# Heuristic packing algorithm - insert from biggest to smallest, into the biggest space
Items = sorted([i for i in Count for j in range(Count[i])],reverse=True)

Boxes = [[]]

for i in Items:
    size,pos = min((sum(p),n) for n,p in enumerate(Boxes))
    if Capacity - size >= i:
        Boxes[pos].append(i)
    else:
        Boxes.append([i])

K = range(len(Boxes))

print('Heuristic box count = ', len(Boxes))
