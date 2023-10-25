from typing import Dict, Tuple
from gurobipy import Model, quicksum, GRB

Data = [
    "6   6    4",
    "     6    ",
    "  3    5  ",
    "   7  9   ",
    " 5  3    5",
    "5    5  2 ",
    "   2  4   ",
    "  7    4  ",
    "    2     ",
    "5    6   6",
]

D = [(0, 1), (0, -1), (1, 0), (-1, 0)]
n = len(Data)
N = range(n)

# Set of seeds

Board = set((i, j) for i in N for j in N)


def Move(s, k, d):
    return (s[0] + k * d[0], s[1] + k * d[1])


n = len(Data)
N = range(n)

Seeds = {(i, j): int(Data[i][j]) for i in N for j in N if Data[i][j] != " "}

m = Model("Cave")


# Variables

X = {(s): m.addVar(vtype=GRB.BINARY) for s in Board}

Y = {
    (s, k, d): m.addVar(vtype=GRB.BINARY)
    for s in Seeds
    for k in range(Seeds[s])
    for d in D
    if Move(s, k, d) in Board
}

# Constraints

OneEachDirection = {
    (s, d): m.addConstr(
        quicksum(Y[s, k, d] for k in range(Seeds[s]) if (s, k, d) in Y) == 1
    )
    for s in Seeds
    for d in D
}

CorrectTotal = {
    s: m.addConstr(
        quicksum(k * Y[s, k, d] for k in range(Seeds[s]) for d in D if (s, k, d) in Y)
        == Seeds[s] - 1
    )
    for s in Seeds
}

YXOff = {
    (s, k, d): m.addConstr(
        quicksum(Y[s, kd, d] for kd in range(k, Seeds[s]) if (s, kd, d) in Y)
        <= 1 - X[Move(s, k, d)]
    )
    for (s, k, d) in Y
}

YOn = {
    (s, k, d): m.addConstr(Y[s, k, d] <= X[Move(s, k + 1, d)])
    for (s, k, d) in Y
    if Move(s, k + 1, d) in Board
}

m.optimize()

for i in range(n):
    for j in range(n):
        if Data[i][j] != " ":
            # Print number
            print(Data[i][j], end="")
        elif X[i, j].X > 0.5:
            # print block
            print("█", end="")
        else:
            print("_", end="")
    print()
