from gurobipy import GRB, quicksum, Model
import random
from colorama import init, Fore

# Initialize colorama
init()

# Size of board
nMax = 10
N = range(nMax)
# Max time
T = range(8)
# Number of vehicles
V = range(6)


def Neighbours(s):
    i, j = s
    tList = []
    if i > 0:
        tList.append((i - 1, j))
    if i < nMax - 1:
        tList.append((i + 1, j))
    if j > 0:
        tList.append((i, j - 1))
    if j < nMax - 1:
        tList.append((i, j + 1))
    return tList


random.seed(5)
C = [[random.randint(0, 4) for j in N] for i in N]

for c in C:
    print(c)

# Sets
# Squares
S = [(i, j) for i in N for j in N]

# Neighbours of square s
Neighs = {s: Neighbours(s) for s in S}

# Data
P = {s: C[s[0]][s[1]] for s in S}

# Model
m = Model("VehicleCollect")

# Variables

X = {(v, s, t): m.addVar(vtype=GRB.BINARY) for v in V for s in S for t in T}

# Constraints

VisitAtMostOnce = {
    s: m.addConstr(quicksum(X[v, s, t] for t in T for v in V) <= 1) for s in S
}

OneSquarePerTurnPerVehicle = {
    (t, v): m.addConstr(quicksum(X[v, s, t] for s in S) == 1) for t in T for v in V
}

MoveToNeigh = {
    (v, s, t): m.addConstr(
        X[v, s, t] <= quicksum(X[v, s_prime, t + 1] for s_prime in Neighs[s])
    )
    for v in V
    for s in S
    for t in T
    if t != T[-1]
}

# Objective

m.setObjective(
    quicksum(X[v, s, t] * P[s] for v in V for t in T for s in S), GRB.MAXIMIZE
)


# Optimise

m.optimize()

colours = [Fore.GREEN, Fore.CYAN]

# Print output
print("_" * (nMax + 2))
for i in N:
    print("|", end="")
    for j in N:
        s = (i, j)
        # Loop over vehicles
        printedSquare = False
        for v in V:
            if sum(X[v, s, t].x for t in T) > 0.9:
                # Vehicle visited this square
                # Print in colour
                print(colours[v] + str(P[s]) + Fore.WHITE, end="")
                printedSquare = True
        if not printedSquare:
            printedSquare = True
            # Print in white
            print(str(P[s]), end="")
    print("|")
print("-" * (nMax + 2))
