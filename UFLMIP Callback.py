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

m._bestSol = GRB.INFINITY

def Callback(model,where):
    if where == GRB.Callback.MIPNODE and \
    model.cbGet(GRB.Callback.MIPNODE_STATUS) == GRB.OPTIMAL and \
    m._bestSol < model.cbGet(GRB.Callback.MIPNODE_STATUS) - epsilon:
        model.cbSetSolution([Y[i] for i in I], [model._bestY[i] for i in I])
        model.cbSetSolution([Theta[j] for j in J], [model._bestTheta[j] for j in J])
    if where==GRB.Callback.MIPSOL:
        YV = model.cbGetSolution(Y)
        ThetaV = model.cbGetSolution(Theta)

        iSet = [i for i in I if YV[i] > 0.9]
        tFun = [min(C[i][j] for i in iSet) for j in J]
        curObjVal = sum(F[i] for i in iSet) + sum(tFun)
        if curObjVal < model._bestSol - epsilon:
            print("Found better solution", curObjVal)
            model._bestSol = curObjVal
            model._bestY = YV

            model._bestTheta = tFun
        for j in J:
            # If ThetaV[j] underestimates
            if ThetaV[j] < tFun[j] - epsilon:       # Epsilon is tolerance
                model.cbLazy(Theta[j] >= tFun[j] - quicksum(Y[i]*(tFun[j]-C[i][j]) for i in I if C[i][j] < tFun[j]))

m.setParam('LazyConstraints',1)
m.optimize(Callback)


