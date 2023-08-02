import gurobipy as gp
# from pathlib import Path
import matplotlib.pyplot as plt
# import sys
# import csv

# Plot a solution
def PlotBoard(Sol, Pre):
    plt.figure(figsize=(len(Pre), len(Pre)), dpi=300)
    plt.pcolormesh(Sol, cmap='Blues', alpha=0.7, edgecolors='k', linewidth=2)
    plt.axis(False)
    for i in N:
        for j in N:
            if Sol[i][j] > 0.9:
                plt.text(j+.5, i+.5, str(Sol[i][j]), ha='center', 
                         va='center', fontsize='x-large', fontweight='black')
            if Pre[i][j] == 0:
                plt.text(j+.5, i+.5, "O", ha='center', va='center',
                         fontsize='x-large', fontweight='black')
    plt.show()


if False:
    K = range(6)
    Pre = [
        [-1, 2,-1, 0,-1,-1],
        [-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1],
        [-1,-1, 0,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1]]

else:
    K = range(10)
    Pre = [
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1, 1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1, 2,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1, 0,-1,-1,-1, 0],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]]


# Create model
Model = gp.Model("SnakeLazy")
Model.setParam("Seed", 0)

# Board indices
N = range(len(Pre))

# Plot blank board
PlotBoard(Pre, Pre)

# Set of squares
S = [(i, j) for i in N for j in N]

# Neighbours
def GetNeigh(i, j):
    return set(S).intersection(
        {(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)})

# Generate sets of neighbours
Neigh = {(i, j): list(GetNeigh(i, j)) for i in N for j in N}


# --- Variables ---
X = {(s, k): Model.addVar(vtype=gp.GRB.BINARY) for s in S for k in K}


# --- Constraints ---
OnePerSquare = {s: Model.addConstr(gp.quicksum(
    X[s, k] for k in K)==1) for s in S}


PreAssign = {(i, j): Model.addConstr(
    X[(i, j), Pre[i][j]]==1) for (i, j) in S if Pre[i][j] >= 0}

MatchK = {k: Model.addConstr(gp.quicksum(
    X[s, k] for s in S)==k) for k in K[1:]}
    
CompatibleNeighbour = {(s, k, ss): Model.addConstr(
    X[s, k] + gp.quicksum(X[ss, kk] for kk in K[1:] if kk != k) <= 1)
    for s in S for k in K[1:] for ss in Neigh[s]}
    
AtLeastOneNeighbour = {(s, k): Model.addConstr(X[s, k] <= gp.quicksum(
    X[ss, k] for ss in Neigh[s])) for s in S for k in K[2:]}

HandleSnakeEnds = {(i, j): Model.addConstr(gp.quicksum(
    X[ss, 0] for ss in Neigh[(i, j)]) == 1) for (i, j) in S if Pre[i][j] == 0}

ZeroNeighUpper = {(i, j): Model.addConstr(gp.quicksum(
    X[ss, 0] for ss in Neigh[(i, j)]) <= 4 - 2*X[(i, j), 0])
    for (i, j) in S if Pre[i][j] == -1}

ZeroNeighLower = {(i,j): Model.addConstr(gp.quicksum(
    X[ss, 0] for ss in Neigh[(i, j)]) >= 2*X[(i, j), 0])
    for (i, j) in S if Pre[i][j] == -1}

# --- Flow model ---
# Source variables
Y = {(s, k): Model.addVar(vtype=gp.GRB.BINARY) for s in S for k in K}

# Flow variables
Z = {(s, ss, k): Model.addVar() for s in S for k in K for ss in Neigh[s]}

# Amounts of flow
Size = {k: k for k in K}
Size[0] = len(N)*len(N) - sum(K)

# Maximum outflow if type k from square s
OutFlowCap = {(s, k): Model.addConstr(gp.quicksum(
    Z[s, ss, k] for ss in Neigh[s]) <= (Size[k] - 2)*X[s, k] + Y[s, k])
    for (s, k) in X}
    
# Flow conservation
FlowCon = {(s, k): Model.addConstr(Size[k] * Y[s, k] + 
    gp.quicksum(Z[ss, s, k] for ss in Neigh[s]) -
    gp.quicksum(Z[s, ss, k] for ss in Neigh[s]) == X[s, k]) for (s, k) in X}

# Can only be source if we have type
YLessThanX = {(s, k): Model.addConstr(Y[s, k] <= X[s, k]) for (s, k) in X}
    
# One source for each type
OneYperK = {k: Model.addConstr(gp.quicksum(
    Y[s, k] for s in S) == 1) for k in K}


# Solve model
Model.optimize()


# Get solution
Solution = [[min(k for k in K if X[(i, j), k].x > 0.9) for j in N] for i in N]
PlotBoard(Solution, Pre)


# # Store solution
# SolutionFile = Path(__file__).parent / "Flow.csv"
# with open(SolutionFile, 'a', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow([str(round(Model.Runtime, 2))])


