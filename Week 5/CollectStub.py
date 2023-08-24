from gurobipy import Model, GRB, quicksum
import random

# Size of board
nMax = 10
N = range(nMax)
# Max time
T = range(8)
# Number of vehicles
V = range(2)

# Set of squares
S = {(i,j) for i in N for j in N}

def Neighbours(s):
    i,j = s
    tList = []
    if i > 0:
        tList.append((i-1,j))
    if i < nMax - 1:
        tList.append((i+1, j))
    if j > 0:
        tList.append((i,j-1))
    if j < nMax - 1:
        tList.append((i, j+1))
    return tList

random.seed(5)
# Random values for each square in the grid
C = [[random.randint(0,4) for j in N] for i in N]

for c in C:
    print (c)


m = Model("CollectPoints")


# Variables
# 1 if vehicle v visits square s in time period t
X = {(s,v,t): m.addVar(vtype=GRB.BINARY) for s in S for v in V for t in T}

# Objectivbe

m.setObjective(quicksum(C[s[0]][s[1]] * X[s,v,t] for s in S for v in V for t in T), GRB.MAXIMIZE)

# Constraints

OneSqPerVT = {(v,t): m.addConstr(quicksum(X[s,v,t] for s in S) == 1) for v in V for t in T}

TravelToNeighbour = {(v, t, s): m.addConstr(X[s,v,t+1] <= quicksum(X[s_prime, v, t] for s_prime in Neighbours(s))) for v in V for t in T[:-1] for s in S}

# Each square's points can only be collected by one vehicle for all time periods
VisitEachSquareOnce = {s: m.addConstr(quicksum(X[s,v,t] for t in T for v in V) <= 1) for s in S}

# Optimise
m.optimize()

print("Objective value: " + str(m.objVal))

print()

for i, line in enumerate(N):
    for j in N:
        p = False
        for v in V:
            for t in T:
                if X[(i,j),v,t].x > 0.9:
                    print(v, end='')
                    p = True
        if not p:
            print('_', end='')
            p = False
    print()