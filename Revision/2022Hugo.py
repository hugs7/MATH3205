from gurobipy import Model, GRB, quicksum
import random
import itertools

# Range of possible sizes - 21 to 50
Size = range(21, 51)

Capacity = 120

# At least one item of each Size
Count = {s: 1 for s in Size}

nItems = 200  # Total number of items

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

K = range(len(Boxes))
B = K
print("Heuristic box count = ", len(Boxes))

naive = False

if naive:
    m = Model("Packing")

    # Variables

    X = {(w, b): m.addVar(vtype=GRB.INTEGER) for w in Count.keys() for b in B}

    Y = {b: m.addVar(vtype=GRB.BINARY) for b in B}

    # Objective

    m.setObjective(quicksum(Y[b] for b in B), GRB.MINIMIZE)

    # Constraints

    # Box used if at least 1 item in it
    # Also set weight limit in the same constraint
    # this links X and Y

    BoxUsed = {
        b: m.addConstr(quicksum(w * X[w, b] for w in Count.keys()) <= Y[b] * Capacity)
        for b in B
    }

    # Pack all items

    PackAll = {
        w: m.addConstr(quicksum(X[w, b] for b in B) == Count.get(w))
        for w in Count.keys()
    }

    # Optimise

    m.optimize()

    # Print solution
    print("Best objective", m.objVal)

    # Print way of packing the boxes

    for b in B:
        print("Box", b, "weight", sum(w * X[w, b].x for w in Count.keys()))
        for w in Count.keys():
            if X[w, b].x > 0.99:
                print("     pack", int(X[w, b].x), "item(s) of weight", w, "kg")
        print()


else:
    # Define set of combinations to pack boxes. This is kinda data I guess
    G: list[list[int]] = []

    for numItems in range(1, 5 + 1):
        print(numItems)
        tmp = itertools.combinations_with_replacement(Size, numItems)

        # Check if the combination is valid. That is it doesn't exceed weight limit
        for combination in tmp:
            if sum(combination) > Capacity:
                continue

            # Convert to binary tuple
            binVec = [0 for _ in range(len(Size))]
            for i in combination:
                binVec[i - 21] += 1

            G.append(binVec)

    # Set of C is length of G
    C = range(len(G))

    m = Model("Packing Fast")

    # Variables

    X = {(b, c): m.addVar(vtype=GRB.BINARY) for b in B for c in C}
    print("Variables defined")
    # Objective

    m.setObjective(quicksum(X[b, c] for b in B for c in C), GRB.MINIMIZE)
    print("Objective defined")
    # Constraints
    # One combination at most per box
    OnePerBox = {b: m.addConstr(quicksum(X[b, c] for c in C) <= 1) for b in B}

    # num items equals num packed
    NumItems = {
        w: m.addConstr(
            quicksum(G[c][w - 21] * X[b, c] for c in C for b in B) == Count[w]
        )
        for w in Count.keys()
    }

    print("Constraints defined")

    # Optimise
    m.optimize()
