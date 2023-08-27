from gurobipy import Model, GRB, quicksum
import random

# Size of board
nMax = 20
N = range(nMax)
# Max time
T = range(13)
# Number of vehicles
V = range(6)

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

# for c in C:
#     print (c)

# Generate paths
from functools import lru_cache

@lru_cache(maxsize=None)
def generate_paths(t, p):
    if t == 0:
        return {(frozenset((p,)), p)}
    
    new_paths = set()
    for s in Neighbours(p):
        new_paths.update({(frozenset(new_p[0] | {s}), s) for new_p in generate_paths(t - 1, s)})
    
    return new_paths

Paths = [generate_paths(t, s) for t in T]
P = set(p[0] for p in Paths[T[-1]])
print(len(P))
m = Model("CollectPoints")


# Variables
# 1 if vehicle v visits square s in time period t
# X = {(s,v,t): m.addVar(vtype=GRB.BINARY) for s in S for v in V for t in T}
Z = {p: m.addVar(vtype=GRB.BINARY) for p in P}
print("Z Created")

# Objective

# m.setObjective(quicksum(C[s[0]][s[1]] * X[s,v,t] for s in S for v in V for t in T), GRB.MAXIMIZE)
m.setObjective(quicksum(sum(C[s[0]][s[1]] for s in p)*Z[p] for p in P), GRB.MAXIMIZE)

# Constraints

ChooseV = m.addConstr(quicksum(Z[p] for p in P) == len(V))

ZVisit = {s: [] for s in S}
for p in P:
    for s in p:
        ZVisit[s].append(Z[p])


# OneSqPerVT = {(v,t): m.addConstr(quicksum(X[s,v,t] for s in S) == 1) for v in V for t in T}
OneSqPerVT = {s: m.addConstr(quicksum(ZVisit[s])<=1) for s in S}


# TravelToNeighbour = {(v, t, s): m.addConstr(X[s,v,t+1] <= quicksum(X[s_prime, v, t] for s_prime in Neighbours(s))) for v in V for t in T[:-1] for s in S}

# Each square's points can only be collected by one vehicle for all time periods
# VisitEachSquareOnce = {s: m.addConstr(quicksum(X[s,v,t] for t in T for v in V) <= 1) for s in S}

# Optimise
m.optimize()

print("Objective value: " + str(m.objVal))

print()

# for i, line in enumerate(N):
#     for j in N:
#         p = False
#         for v in V:
#             for t in T:
#                 if X[(i,j),v,t].x > 0.9:
#                     print(v, end='')
#                     p = True
#         if not p:
#             print('_', end='')
#             p = False
#     print()

Veh = [['_' for _ in N] for _ in N]

count = 0
for p in P:
    if Z[p].x > 0.9:
        for s in p:
            Veh[s[0]][s[1]] = str(count)

        count += 1
        
        
for i, line in enumerate(N):
    for j in N:
        print(Veh[i][j], end='')
    print()