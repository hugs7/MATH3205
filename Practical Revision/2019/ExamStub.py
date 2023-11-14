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

# Set of all possible rows for row i
print("Generating rows...")
R = {i: set(itertools.permutations(K)) for i in N}
newR = {i: set() for i in N}
# Filter out rows that don't match the preset in the grid
for row in R:
    removed = 0
    for index in N:
        if Grid[row][index] != 0:
            # We have a preset value
            # Loop over all possile values and remove any that don't have a matching
            # value at this index
            for comb in R[row]:
                if comb[index] != Grid[row][index]:
                    #     R[row].remove(comb)
                    removed += 1
                else:
                    newR[row].add(comb)

    print(row, "removed", removed)

print("Generating columns...")
# Set of all possible columns for column j
C = {j: set(itertools.permutations(K)) for j in N}
newC = {j: set() for j in N}
# Filter out columns that don't match the preset in the grid
for col in C:
    removed = 0
    for index in N:
        if Grid[index][col] != 0:
            # We have a preset value
            # Loop over all possile values and remove any that don't have a matching
            # value at this index
            for comb in C[col]:
                if comb[index] != Grid[index][col]:
                    #     C[col].remove(comb)
                    removed += 1
                else:
                    newC[col].add(comb)

    print(col, "removed", removed)

m = Model("Skyscrapers")

# Variables
X = {(i, j, k): m.addVar(vtype=GRB.BINARY) for i in N for j in N for k in K}

Y = {(i, p): m.addVar(vtype=GRB.BINARY) for i in N for p in R[i]}
Z = {(j, p): m.addVar(vtype=GRB.BINARY) for j in N for p in C[j]}

# Constraints

# Preset values
Preset = {
    (i, j): m.addConstr(X[i, j, Grid[i][j]] == 1)
    for i in N
    for j in N
    if Grid[i][j] > 0
}

EachCell = {
    (i, j): m.addConstr(quicksum(X[i, j, k] for k in K) == 1) for i in N for j in N
}

EachRow = {i: m.addConstr(quicksum(X[i, j, k] for j in N) == 1) for i in N for k in K}
EachCol = {j: m.addConstr(quicksum(X[i, j, k] for i in N) == 1) for j in N for k in K}

ChooseRow = {i: m.addConstr(quicksum(Y[i, p] for p in R[i]) == 1) for i in N}
ChooseCol = {j: m.addConstr(quicksum(Z[j, p] for p in C[j]) == 1) for j in N}

# SquareMatch = {
#     quicksum(p[j] * Y[p, i] for p in R[i]) == quicksum(p[i] * Z[p, j] for p in C[i])
#     for i in N
#     for j in N
# }

m.optimize()


# Print solution

for i in N:
    for j in N:
        for k in K:
            if X[i, j, k].x > 0.9:
                print(k, end="")
    print()
