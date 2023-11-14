from typing import Dict, Set, Tuple
from gurobipy import GRB, quicksum, Model
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

# Generate some additional sets

print("Generating row combinations...")
# Set of all possible row combinations for each row factoring in the preset grid
R = {i: set(itertools.permutations(K)) for i in N}
# Filter out the row combinations that are not valid for the preset grid
toRemove: Dict[int, Set[Tuple[int, ...]]] = {}
for row in N:
    toRemove[row] = set()
    for comb in R[row]:
        for index, height in enumerate(comb):
            if Grid[row][index] != 0 and Grid[row][index] != height:
                # Found an invalid combination
                # Remove from R[row]
                toRemove[row].add(comb)
                break

        # Remove combinations which don't follow the visible rule
        # Look at left and right [1, 2]
        skipComb = False
        for direction, sign in [(1, 1), (2, -1)]:
            # calculate the number of visible buildings in direction
            visible = 0
            highestBuilding = 0
            for height in comb[::sign]:
                if height > highestBuilding:
                    highestBuilding = height
                    visible += 1

            if visible != Visible[direction][row] and Visible[direction][row] != 0:
                # Found an invalid combination
                # Remove from R[row]
                toRemove[row].add(comb)
                skipComb = True
                break
        if skipComb:
            continue

    # Remove all invalid combinations
    R[row] = R[row] - toRemove[row]

    print(row, len(R[row]))

print("Generating column combinations...")
# Set of all possible column combinations for each column factoring in the preset grid
C = {j: set(itertools.permutations(K)) for j in N}
# Filter out the column combinations that are not valid for the preset grid
toRemove = {}
for col in N:
    toRemove[col] = set()
    for comb in C[col]:
        for index, height in enumerate(comb):
            if Grid[index][col] != 0 and Grid[index][col] != height:
                # Found an invalid combination
                # Remove from C[col]
                toRemove[col].add(comb)
                break

        # Remove combinations which don't follow the visible rule
        # Look at top and bottom [0, 3]
        skipComb = False
        for direction, sign in [(0, 1), (3, -1)]:
            # calculate the number of visible buildings in direction
            visible = 0
            highestBuilding = 0
            for height in comb[::sign]:
                if height > highestBuilding:
                    highestBuilding = height
                    visible += 1

            if visible != Visible[direction][col] and Visible[direction][col] != 0:
                # Found an invalid combination
                # Remove from C[col]
                toRemove[col].add(comb)
                skipComb = True
                break
        if skipComb:
            continue

    # Remove all invalid combinations
    C[col] = C[col] - toRemove[col]

    print(col, len(C[col]))


# Model

m = Model("Skyscrapers")

# Variables

Y = {(p, i): m.addVar(vtype=GRB.BINARY) for i in N for p in R[i]}
Z = {(p, j): m.addVar(vtype=GRB.BINARY) for j in N for p in C[j]}

# No objective

# Constraints

# One combination per row
OnePerRow = {i: m.addConstr(quicksum(Y[p, i] for p in R[i]) == 1) for i in N}

# One combination per column
OnePerCol = {j: m.addConstr(quicksum(Z[p, j] for p in C[j]) == 1) for j in N}

# Each square matches row and column in combination

EachSquare = {
    (i, j): m.addConstr(
        quicksum(p[j] * Y[p, i] for p in R[i]) == quicksum(p[i] * Z[p, j] for p in C[j])
    )
    for i in N
    for j in N
}


m.optimize()

# print solution

for i in N:
    for p in R[i]:
        if Y[p, i].x > 0.9:
            print(p)
