from gurobipy import Model, GRB, quicksum
import itertools

# Store Top, Left, Right, Bottom
Visible = [
    [0, 0, 3, 3, 4, 0, 4, 0],
    [0, 0, 2, 5, 0, 3, 0, 0],
    [4, 0, 0, 3, 3, 0, 2, 0],
    [3, 5, 0, 0, 3, 3, 1, 0],
]

Grid = [
    [0, 0, 0, 0, 3, 0, 0, 0],
    [0, 1, 0, 4, 0, 0, 0, 0],
    [0, 6, 0, 0, 1, 0, 0, 0],
    [0, 0, 6, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

nGrid = len(Grid)

N = range(nGrid)
K = range(1, nGrid + 1)

# You may find itertools.permutations useful for part d
# You can use it like this "for r in itertools.permutations(K)"

m = Model("Sudoku")

# Variables
X = {(i, j, k): m.addVar(vtype=GRB.BINARY) for i in N for j in N for k in K}

# Constraints

EachCell = {
    (i, j): m.addConstr(quicksum(X[i, j, k] for k in K) == 1) for i in N for j in N
}

EachRow = {i: m.addConstr(quicksum(X[i, j, k] for j in N) == 1) for i in N for k in K}
EachCol = {j: m.addConstr(quicksum(X[i, j, k] for i in N) == 1) for j in N for k in K}


m.optimize()


# Print solution

for i in N:
    for j in N:
        for k in K:
            if X[i, j, k].x > 0.9:
                print(k, end="")
    print()
