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

# Set of possible paths

G = set()


def growPath(subPath, tail, lengthRemaining, neighbours):
    # print(word, endPosition, lengthRemaining)
    if lengthRemaining == 0:
        # Convert list of positions to string
        # Add to list of generated words
        G.add(tuple(subPath))
    else:
        if len(subPath) == 0 or tail is None:
            # loop over the starting squares
            for startingSquare in S:
                # Add position to list
                newPartWordPositions = subPath + [startingSquare]
                # Recurse
                growPath(
                    newPartWordPositions,
                    startingSquare,
                    lengthRemaining - 1,
                    neighbours,
                )
        else:
            for childPosition in neighbours[tail]:
                if childPosition in subPath:
                    # can't use this neighbour as position is already used
                    continue

                # Add the neighbour to the list of positions
                newPartWordPositions = subPath + [childPosition]

                # can use this neighbour
                # Recurse
                growPath(
                    newPartWordPositions,
                    childPosition,
                    lengthRemaining - 1,
                    neighbours,
                )


growPath([], None, T[-1] + 1, Neighs)

print("Number of possible paths", len(G))

# Data
P = {s: C[s[0]][s[1]] for s in S}

# Model
m = Model("VehicleCollectD")
print("Defined model")
# Variables

X = {(v, g): m.addVar(vtype=GRB.BINARY) for v in V for g in G}
print("Defined variables")
# Constraints
ChooseOnePath = {v: m.addConstr(quicksum(X[v, g] for g in G) == 1) for v in V}

VisitAtMostOnce = {
    s: m.addConstr(quicksum(X[v, g] for v in V for g in G if s in g) <= 1) for s in S
}
print("Defined Constraints")
# Objective

m.setObjective(
    quicksum(quicksum(P[s] for s in g) * X[v, g] for v in V for g in G), GRB.MAXIMIZE
)
print("Defined objective")


# Optimise

m.optimize()

colours = [Fore.GREEN, Fore.CYAN, Fore.RED, Fore.MAGENTA, Fore.YELLOW, Fore.BLUE]

# Print output
chosenPaths = []
# Determine paths chosen by each vehicle
for v in V:
    for g in G:
        if X[v, g].x > 0.9:
            chosenPaths.append(g)
            break

print("_" * (nMax + 2))
for i in N:
    print("|", end="")
    for j in N:
        s = (i, j)
        # Loop over vehicles
        printedSquare = False
        for v in V:
            if s in chosenPaths[v]:
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
