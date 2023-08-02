import math
import random
from gurobipy import Model, GRB, quicksum

random.seed(3)

epsilon = 1e-6

nLocs = 300
I = range(nLocs)
J = range(nLocs)
F = [random.randint(10000,20000) for i in I]
C = [[random.randint(1000,2000) for j in J] for i in I]

m = Model()

Y = {i: m.addVar(vtype=GRB.BINARY) for i in I}

# Additional Variable
# Set lower bound
Theta = {j: m.addVar(lb=min(C[i][j] for i in I))  for j in J}

m.setObjective(quicksum(F[i]*Y[i] for i in I) +
               quicksum(Theta[j] for j in J))

# Must open at least one facility
m.addConstr(quicksum(Y[i] for i in I) >= 1)

m.setParam('MIPGap',0)
# m.setParam('Threads',8)

m.setParam('OutputFlag', 0)
for index in range(10):
    m.optimize()
    iSet = [i for i in I if Y[i].x > 0.9]
    tFun = [min(C[i][j] for i in iSet) for j in J]
    print(f"{m.runTime:< 5}, {m.objVal:<10}, {sum(F[i] for i in iSet) + sum(tFun)}")
    for j in J:
        # If Theta[j] underestimates
        if Theta[j].x < tFun[j] - epsilon:       # Epsilon is tolerance
            m.addConstr(Theta[j] >= tFun[j] - quicksum(Y[i]*(tFun[j]-C[i][j]) for i in I if C[i][j] < tFun[j]))
