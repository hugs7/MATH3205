import matplotlib.pyplot as plt
from gurobipy import GRB, Model, quicksum


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

# Variable X is binary. It says for each square and each number, k, is that square turned on
X = {(s,k): m.addVar(vtype=GRB.BINARY) for s in S for k in K}

# Constraints
# If we sum over all the k's, for each square, exactly 1 can be turned on.
# Exactly 1 because k = 0 means the path of the snake
OneValPerSq = {s:
               m.addConstr(quicksum(X[s,k] for k in K) == 1)
               for s in S
               }

# Set pre-assignments for s: (i,j) to be 1 for that k for each row and column if >= 0
PreAssign = {(i, j):
               m.addConstr(X[(i,j), Pre[i][j]] == 1)
               for i in N for j in N if Pre[i][j] >= 0}

# For each k, we must have exactly k squares turned on which are that k
KItemsOfTypeK = {k:
                 m.addConstr(quicksum(X[s,k] for s in S) == k)
                 for k in K[1:]
                 }

# {s: 
#  m.addConstr(X[s,k] <= quicksum(X[s_prime, k] for s_prime in GetNeigh(*s))) for s in S for k in K if k >= 2 }

# For each k, and for each square, s, the neighbours of that square, s_primes, must not be of a different k value.
# So this is done by saying either the square s for K=k is on OR if you sum over the other k values greater than 1, at most one of them will be on.
# By using an exclusive OR here, this prevents K=k from being a neighbour of K!=k
DifferentKsNotTouching = {(s, s_prime, k):
                          m.addConstr(X[s,k] + quicksum(X[s_prime, k_prime] for k_prime in K if k_prime >= 1 and k_prime != k)
                                       <= 1) for s in S for s_prime in Neigh[s] for k in K if k >= 1}

# For each square, s, and each k greater than or equal to 2, the sum of the neighbours must be greater than s
# This ensures squares of the same k must be turned on next to each other in at least groups of 2.
# It cannot ensure that groups of k > 2 stick together.
TouchTheSameK = {(s,k):
                 m.addConstr(X[s,k] <= quicksum(X[s_prime, k] for s_prime in Neigh[s]))
                 for s in S for k in K if k >= 2}

# --- Snake Path Constraints ---
# Ensures at each end of the path, signified by 0, there is exactly one path next to it.
# For each square which is the end point (only two squares), the sum of X[s,0] for the 
# neighbouring squares must be == 1
OnePathTouchesEnds = {(x,y):
                      m.addConstr(quicksum(X[s,0] for s in Neigh[x,y]) == 1)
                                  for x in N for y in N if Pre[x][y]==0}

# For all squares, (x,y) not pre-defined (excluding endpoints), the path neighbours must be at 
# least 0 if not on path and at least 2 if on path
NeighboursOfPathA = {(x,y):
                     m.addConstr(quicksum(X[s,0] for s in Neigh[(x,y)]) >= 2*X[(x,y),0]) 
                     for x in N for y in N if Pre[x][y] < 0}

# For all squares, (x,y) not pre-defined (excluding endpoints), the path neighbours must be at 
# most 4 if not on path and at most 2 if on path
NeighboursOfPathB = {(x,y):
                     m.addConstr(quicksum(X[s,0] for s in Neigh[(x,y)]) <= 4 - 2*X[(x,y),0]) 
                     for x in N for y in N if Pre[x][y] < 0}

# With the above two constraints, we bound above and below that all points on the path 
# (excluding end-points), must have exactly 2 neighbours on the path
# This ensures the path does not split.

# m.optimize()
# Sol = [[min(k for k in K if X[(i,j),k].x >= 0.9) for j in N] for i in N]
# PlotBoard(Sol, Pre)


# EnoughNeighboursCloseEnough = {
#     (s,k):
#     m.addConstr(quicksum(X[s_prime,k] for s_prime in S if abs(s[0]-s_prime[0])+abs(s[1]-s_prime[1]) <= k-1) >= k * X[s,k])
#     for s in S for k in K if k >= 4
# }


def FindSet(i,j, k,Sol):
    # Set this square to inactive in the solution. This is so we don't start another cluster.
    Sol[i][j] = -1

    # Initialise the cluster to this square
    clusterSet = {(i,j)}

    # For squares in (i,j)'s neighbourhood
    for (ii, jj) in Neigh[i,j]:
        # If a neighbour has the same k value (is turned on)
        if Sol[ii][jj] == k:
            # Add to the tSet the set of neighbours of that square, (ii, jj)
            clusterSet |= FindSet(ii,jj,k, Sol)
    
    # When there are no more neighbours to find, return tSet

    return clusterSet

def calculateSol(X):
    return [[min(k for k in K if X[(i,j),k] >= 0.9) for j in N] for i in N]

def callback(model, where):
    if where == GRB.Callback.MIPSOL:
        print("Callback Actual")
        # Get Current Solution from Gurobi
        XV = model.cbGetSolution(X)

        # Calculate solution 2D list
        Sol = calculateSol(XV)
        PlotBoard(Sol, Pre)
        # Our aim is to find clusters of a given k. For each square (i,j) in the grid, we find 
        # a cluster of neighbours of that k value. Duplicate clusters are avoided in the recursive
        # function.
        KSets = [[] for k in K]
        for i in N:
            for j in N:
                k = Sol[i][j]
                if k >= 0:
                    KSets[k].append(FindSet(i,j,k, Sol))

        # Then we find all the neightbours for all squares in each of the cluster(s) of k
        # We remove the inner squares (tSet) leaving the neighbours of that cluster.
        # Finally, we add a constraint for each square in the cluster, add a constraint to
        # the model which says the sum of the neighbours of the cluster must be greater
        # than square, s. So either you add one to the neighbour set, nSet or you turn off
        # the square, s. Very clever.
        for k in K:
            if len(KSets[k]) <= 1:
                continue
            for clusterSet in KSets[k]:
                # nSet is the set of Neighbours
                nSet = set()
                for s in clusterSet:
                    nSet |= Neigh[s]
                nSet -= clusterSet
                for s in clusterSet:
                    model.cbLazy(XV[s,k] <= 
                                quicksum(XV[s_prime,k] for s_prime in nSet)
                                )



m.setParam('LazyConstraints', 1)
m.optimize(callback)
# Sol = calculateSol(X)
# PlotBoard(Sol, Pre)
