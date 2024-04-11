from gurobipy import quicksum, GRB, Model
import random
from scipy.stats import binom
from math import log, exp

# Range of possible sizes - 21 to 50
Size = range(21, 51)

part = 4

Capacity = 120

# At least one item of each Size
Count = {s: 1 for s in Size}


if part == 1:
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

    K = range(len(Boxes))

    Iset = {(s, i) for s in Count for i in range(Count[s])}
    assert len(Iset) == len(Items)

    print("Heuristic box count = ", len(Boxes))

    m = Model()

    X = {(i, b): m.addVar(vtype=GRB.BINARY) for i in Iset for b in K}
    Y = {b: m.addVar(vtype=GRB.BINARY) for b in K}

    m.setObjective(quicksum(Y[b] for b in K))

    BoxCapacity = {
        b: m.addConstr(quicksum(i[0] * X[i, b] for i in Iset) <= Y[b] * Capacity)
        for b in K
    }

    EachItemBoxed = {i: m.addConstr(quicksum(X[i, b] for b in K) == 1) for i in Iset}

    m.optimize()

    print(m.objval)

elif part == 3:
    nItems = 200

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

    Iset = {(s, i) for s in Count for i in range(Count[s])}
    assert len(Iset) == len(Items)

    print("Heuristic box count = ", len(Boxes))

    def DistinctBoxes(biggest=0, capacity=Capacity):
        if biggest > capacity:
            return [[]]
        return [
            [s] + k
            for s in Size
            if s >= biggest and s <= capacity
            for k in DistinctBoxes(s, capacity - s)
        ]

    B = {tuple(x) for x in DistinctBoxes()}

    def countEq(iter, x):
        return sum(1 for y in iter if y == x)

    m = Model()

    X = {b: m.addVar(vtype=GRB.INTEGER) for b in B}

    m.setObjective(quicksum(X[b] for b in B))

    EachItemBoxed = {
        s: m.addConstr(quicksum(countEq(b, s) * X[b] for b in B) == Count[s])
        for s in Count
    }

    m.optimize()

    print("Heuristic: ", len(Boxes))
    print("Best: ", m.objval)

else:
    nItems = 200

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

    Iset = {(s, i) for s in Count for i in range(Count[s])}
    assert len(Iset) == len(Items)

    print("Heuristic box count = ", len(Boxes))

    def DistinctBoxes(biggest=0, capacity=Capacity):
        if biggest > capacity:
            return [[]]
        return [
            [s] + k
            for s in Size
            if s >= biggest and s <= capacity
            for k in DistinctBoxes(s, capacity - s)
        ]

    B = {tuple(x) for x in DistinctBoxes()}

    def countEq(iter, x):
        return sum(1 for y in iter if y == x)

    # Dictionary of probabilities of boxes weighing more than Capacity
    ProbSatisfiesCapacity = {b: binom.cdf(Capacity - sum(b), len(b), 0.1) for b in B}

    # Fix some number of boxes
    NumBoxes = 59

    m = Model()

    X = {b: m.addVar(vtype=GRB.INTEGER) for b in B}

    m.setObjective(
        quicksum(log(ProbSatisfiesCapacity[b]) * X[b] for b in B), GRB.MAXIMIZE
    )

    EachItemBoxed = {
        s: m.addConstr(quicksum(countEq(b, s) * X[b] for b in B) == Count[s])
        for s in Count
    }

    LimitOnBoxes = m.addConstr(quicksum(X[b] for b in B) <= NumBoxes)

    m.optimize()

    print(
        "Best probability: ",
        exp(sum(log(ProbSatisfiesCapacity[b]) * X[b].x for b in B)),
    )
