import matplotlib.pyplot as plt
from ortools.sat.python import cp_model
# import gurobipy as gp
import numpy as np
import time



# Plot a solution
def PlotBoard(Sol, Pre):
    plt.figure(figsize=(len(Pre), len(Pre)), dpi=300)
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

# # Plot blank board
# PlotBoard([[(Pre[i][j] if (Pre[i][j]>=0) else 0) for j in N] for i in N], Pre)

# Set of squares
S = {(i, j) for i in N for j in N}

# Neighbours
def GetNeigh(i, j):
    return S.intersection(
        {(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)})

# Generate sets of neighbours
Neigh = {s: GetNeigh(*s) for s in S}

# Constraint Programming model
CP = cp_model.CpModel()

# Variables
X = {(s, k): CP.NewBoolVar(f"X({s}, {k})") for s in S for k in K}

# Each square has one value
for s in S:
    CP.AddExactlyOne(X[s, k] for k in K)

# Fix pre squares
for (i, j) in S:
    if Pre[i][j] >= 0:
        CP.Add(X[(i, j), Pre[i][j]] == 1)

# k squares of type k
for k in K[1:]:
    CP.Add(sum(X[s, k] for s in S) == k)
    
# At least one neighbor of same type
for s in S:
    for k in K[2:]:
        CP.AddBoolOr(X[ss, k] for ss in Neigh[s]).OnlyEnforceIf(X[s, k])

# No neighbors of different type
for s in S:
    for k in K[1:]:
        CP.AddBoolAnd(X[ss, kk].Not() for ss in Neigh[s] for kk in K[1:] if kk != k).OnlyEnforceIf(X[s, k])

# Snake structure
for (i, j) in S:
    if Pre[i][j] == 0:
        CP.AddExactlyOne(X[ss, 0] for ss in Neigh[(i, j)])
    else:
        CP.Add(sum(X[ss, 0] for ss in Neigh[(i, j)]) == 2).OnlyEnforceIf(X[(i, j), 0])

# Expand set function
def FindSet(i, j, k, Sol):
    Sol[i][j] = -1
    tSet = {(i, j)}
    for (ii, jj) in Neigh[(i, j)]:
        if Sol[ii][jj] == k:
            tSet |= FindSet(ii, jj, k, Sol)
    return tSet

# Timekeeping
StartTime = time.time()
Runs = 0

# Connectivity
while True:
    Runs += 1

    # Solve the problem
    solver = cp_model.CpSolver()
    status = solver.Solve(CP)
            
    # If the problem is infeasible
    if status == cp_model.INFEASIBLE:
        print("INFEASIBLE")
        break
    
    # Stopping condition
    stop = True
    
    # If the problem is solved
    if status == cp_model.OPTIMAL:
        
        # Solution
        Sol = [[0 for j in N] for j in N]
        for s in S:
            for k in K:
                if solver.Value(X[s, k]) > 0.9:
                    Sol[s[0]][s[1]] = k
    
        # Generate the k sets
        KSets = [[] for k in K]
        for (i, j) in S:
            k = Sol[i][j]
            if k >= 0:
                KSets[k].append(FindSet(i, j, k, Sol))
        
        # Iterate eggs
        for k in K:
            
            # If egg is broken...
            if len(KSets[k]) > 1:
                stop = False
                
                # Iterate connected region
                for tSet in KSets[k]:
                    
                    # Get region
                    tNeigh = set()
                    for (i,j) in tSet:
                        tNeigh |= set(Neigh[(i, j)])
                    tNeigh -= tSet
                    

                    # tNeigh are all the strict neighbours of tSet
                    for s in tSet:
                        CP.AddBoolOr(X[ss, k] for ss in tNeigh).OnlyEnforceIf(X[s, k])
        
        # Stop
        if stop:
            break
      

# Get total time
TotalTime = time.time() - StartTime
print(TotalTime, Runs)

# Solution
Sol = [[0 for j in N] for j in N]
for s in S:
    for k in K:
        if solver.Value(X[s, k]) > 0.9:
            Sol[s[0]][s[1]] = k
  
# Plot solution
PlotBoard(Sol, Pre)
