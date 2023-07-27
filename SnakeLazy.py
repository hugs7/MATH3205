import matplotlib.pyplot as plt
from gurobipy import *


# Plot a solution
def PlotBoard(Sol, Pre):
    plt.figure(figsize=(len(Pre), len(Pre)), dpi=100)
    plt.pcolormesh(Sol, cmap='tab20', alpha=0.7, edgecolors='k', linewidth=2)
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

# Board indices
N = range(len(Pre))

# Plot blank board
# PlotBoard([[(Pre[i][j] if (Pre[i][j]>=0) else 0) for j in N] for i in N], Pre)

# Set of squares
S = {(i, j) for i in N for j in N}

# Neighbours
def GetNeigh(i, j):
    return S.intersection(
        {(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)})

# Generate sets of neighbours
Neigh = {s: GetNeigh(*s) for s in S}

# Create model
m = Model("Snake")
m.setParam("Seed", 0)

X = {(s,k): m.addVar(vtype=GRB.BINARY) for s in S for k in K}

OneValuePerSquare = {s:
    m.addConstr(quicksum(X[s,k] for k in K)==1)
    for s in S}

PreAssign = {(i,j):
    m.addConstr(X[(i,j),Pre[i][j]]==1)
    for i in N for j in N if Pre[i][j]>=0}
    
KItemsOfTypeK = {k:
    m.addConstr(quicksum(X[s,k] for s in S)==k)
    for k in K[1:]}
    
DifferentKsNotTouching = {(s,sd,k):
    m.addConstr(X[s,k]+quicksum(X[sd,kd] for kd in K[1:] if kd!=k)<=1)
    for s in S for sd in Neigh[s] for k in K[1:]}
    
TouchTheSameK = {(s,k):
    m.addConstr(X[s,k]<=quicksum(X[sd,k] for sd in Neigh[s]))
    for s in S for k in K[2:]}
    
OnePathTouchesEnds = {(i,j):
    m.addConstr(quicksum(X[s,0] for s in Neigh[i,j])==1)
    for i in N for j in N if Pre[i][j]==0}
    
NeighboursOfPathA = {(i,j):
    m.addConstr(quicksum(X[s,0] for s in Neigh[i,j])>=2*X[(i,j),0])
    for i in N for j in N if Pre[i][j]<0}
    
NeighboursOfPathB = {(i,j):
    m.addConstr(quicksum(X[s,0] for s in Neigh[i,j])<=4-2*X[(i,j),0])
    for i in N for j in N if Pre[i][j]<0}
    
# EnoughNeighboursCloseEnough = {(s,k):
#     m.addConstr(quicksum(X[sd,k] for sd in S 
#                 if abs(s[0]-sd[0])+abs(s[1]-sd[1])<=k-1)
#                 >=k*X[s,k])
#     for s in S for k in K[4:]}
    
def FindSet(i,j,k,Sol):
    Sol[i][j] = -1
    tSet = {(i,j)}
    for (ii,jj) in Neigh[i,j]:
        if Sol[ii][jj]==k:
            tSet |= FindSet(ii,jj,k,Sol)
    return tSet

# GSol = None
def Callback(model,where):
    if where==GRB.Callback.MIPSOL:
        XV = model.cbGetSolution(X)
        Sol = [[min(k for k in K if XV[(i,j),k] > 0.9) for j in N] for i in N]
        PlotBoard(Sol, Pre)
        # GSol = Sol
        KSets = [[] for k in K]
        for i in N:
            for j in N:
                if Sol[i][j]>=0:
                    k = Sol[i][j]
                    KSets[k].append(FindSet(i,j,k,Sol))
    
        for k in K:
            if len(KSets[k])>1:
                for tSet in KSets[k]:
                    # nSet are the squares that neighbour tSet
                    nSet = set()
                    for s in tSet:
                        nSet |= Neigh[s]
                    nSet -= tSet
                    for s in tSet:
                        model.cbLazy(X[s,k]<=quicksum(X[sd,k] for sd in nSet))

m.setParam('Threads',8)
m.setParam('LazyConstraints',1)
m.optimize(Callback)
# PlotBoard(GSol, Pre)


# nPass = 0
# RunTime = 0
# while True:
#     m.optimize()
#     nPass += 1
#     RunTime += m.RunTime
#     print(nPass, RunTime)
    
#     Sol = [[min(k for k in K if X[(i,j),k].x > 0.9) for j in N] for i in N]
#     PlotBoard(Sol, Pre)
    
#     KSets = [[] for k in K]
#     for i in N:
#         for j in N:
#             if Sol[i][j]>=0:
#                 k = Sol[i][j]
#                 KSets[k].append(FindSet(i,j,k,Sol))

#     if max(len(KSets[k]) for k in K)==1:
#         break
#     for k in K:
#         if len(KSets[k])>1:
#             for tSet in KSets[k]:
#                 # nSet are the squares that neighbour tSet
#                 nSet = set()
#                 for s in tSet:
#                     nSet |= Neigh[s]
#                 nSet -= tSet
#                 for s in tSet:
#                     m.addConstr(X[s,k]<=quicksum(X[sd,k] for sd in nSet))
        


