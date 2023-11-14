from gurobipy import Model, quicksum, GRB
import os

dirpath = os.path.join("Practical Revision", "2013")

# f = open(os.path.join(dirpath, "flow1.txt"))
f = open(os.path.join(dirpath, "flow2.txt"))

Board = [f.readline().strip()]
N = range(len(Board[0]))

for n in N[1:]:
    Board.append(f.readline().strip())
f.close()

colours = list(set([Board[i][j] for i in N for j in N if Board[i][j] != "-"]))
print("Colours", colours)
C = range(len(colours))

dests: dict[int, tuple[int, int]] = {}
origins: dict[int, tuple[int, int]] = {}

for c in C:
    for i in N:
        for j in N:
            if Board[i][j] == colours[c]:
                # check if origin has been set
                if c not in origins.keys():
                    # Add to origins
                    origins[c] = (i, j)
                else:
                    # Add to dests
                    dests[c] = (i, j)

print("dests", dests)
print()
print("origins", origins)

# Set of squares
S = {(i, j) for i in N for j in N}


# Neighbours
def GetNeigh(i, j):
    return S.intersection({(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)})


# Set of neighbours of each square
Neigh = {(i, j): GetNeigh(i, j) for i in N for j in N}


m = Model("Flow")
# Variables

X = {(s, c): m.addVar(vtype=GRB.BINARY) for s in S for c in C}
Y = {(s1, s2, c): m.addVar(vtype=GRB.BINARY) for s1 in S for s2 in Neigh[s1] for c in C}

# Objective

# No objective

# Constraints

# Each square has exactly one colour
OneColour = {s: m.addConstr(quicksum(X[s, c] for c in C) == 1) for s in S}

# Flow conservation
FlowOut = {
    (s, c): quicksum(Y[s, s2, c] for s2 in Neigh[s])
    for s in S
    for c in C
    if s != dests[c]
}

FlowIn = {
    (s, c): quicksum(Y[s2, s, c] for s2 in Neigh[s])
    for s in S
    for c in C
    if s != origins[c]
}

# Presets

PreSetOrigins = {c: m.addConstr(X[origins[c], c] == 1) for c in C}
PreSetDests = {c: m.addConstr(X[dests[c], c] == 1) for c in C}

# Cut Cycles
Cut2Cycles = {
    (s1, s2): m.addConstr(quicksum(Y[s1, s2, c] + Y[s2, s1, c] for c in C) <= 1)
    for s1 in S
    for s2 in Neigh[s1]
    if s2 > s1
}


def Callback(model, where):
    if where == GRB.Callback.MIPSOL:
        YV = model.cbGetSolution(Y)

        Next = {}
        for s1, s2, k in YV:
            if YV[(s1, s2, k)] > 0.9:
                Next[s1] = s2


m.optimize()


# print solutoin
for i in N:
    for j in N:
        for c in C:
            if X[(i, j), c].x > 0.9:
                print(colours[c], end="")
    print()
