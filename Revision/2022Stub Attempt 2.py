from gurobipy import GRB, quicksum, Model
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
for i in range(nItems - len(Size)):
    Count[random.choice(Size)] += 1

# Heuristic packing algorithm - insert from biggest to smallest, into the biggest space
Items = sorted([i for i in Count for j in range(Count[i])], reverse=True)

Boxes = [[]]

for i in Items:
    size, pos = min((sum(p), n) for n, p in enumerate(Boxes))
    if Capacity - size >= i:
        Boxes[pos].append(i)
    else:
        Boxes.append([i])

B = range(len(Boxes))

print("Heuristic box count = ", len(Boxes))

ItemsIndexed = {i: Items[i] for i in range(len(Items))}

m = Model("Box Packing")

# Variables

X = {(i, b): m.addVar(vtype=GRB.BINARY) for i in ItemsIndexed.keys() for b in B}
Y = {b: m.addVar(vtype=GRB.BINARY) for b in B}

# Objective

m.setObjective(quicksum(Y[b] for b in B), GRB.MINIMIZE)

# Constraints

# Limit weight and link x to y
LimitWeight = {
    b: m.addConstr(
        quicksum(X[i_key, b] * i_val for (i_key, i_val) in ItemsIndexed.items())
        <= Y[b] * Capacity
    )
    for b in B
}

# Use each item once

UseEachOnce = {
    i: m.addConstr(quicksum(X[i, b] for b in B) == 1) for i in ItemsIndexed.keys()
}

# Optimize

m.optimize()

print(m.objval)
exit()

for b in B:
    print(f"Box {b} of weight {sum(i * X[i, b].x for i in ItemsIndexed)}kg.")
    for i in ItemsIndexed:
        if X[i, b].x > 0.5:
            print(f"    Item {i} of weight {i}kg.")

    print()
