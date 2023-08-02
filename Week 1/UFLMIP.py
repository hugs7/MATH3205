import math
import random
from gurobipy import *

random.seed(3)

nLocs = 300
I = range(nLocs)
J = range(nLocs)
F = [random.randint(10000,20000) for i in I]
C = [[random.randint(1000,2000) for j in J] for i in I]

m = Model()

Y = {i: m.addVar(vtype=GRB.BINARY) for i in I}
X = {(i,j): m.addVar(vtype=GRB.BINARY) for i in I for j in J}

m.setObjective(quicksum(F[i]*Y[i] for i in I)+
               quicksum(C[i][j]*X[i,j] for i in I for j in J))

AssignToOne = {j:
    m.addConstr(quicksum(X[i,j] for i in I)==1)
    for j in J}
    
AssignToOpen = {(i,j):
    m.addConstr(X[i,j]<=Y[i])
    for i in I for j in J}

m.setParam('MIPGap',0)
# m.setParam('Threads',8)
m.optimize()