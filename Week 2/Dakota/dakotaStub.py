from gurobipy import Model, quicksum, GRB

EPS = 0.0001

Resources = ["Lumber", "Finishing", "Carpentry"]
Products = ["Desk", "Table", "Chair"]

R = range(len(Resources))
P = range(len(Products))

Cost = [2,4,5.2]
Input = [
        [8,6,1],
        [4,2,1.5],
        [2,1.5,0.5]]

Prob = [0.3,0.4,0.3]
S = range(len(Prob))

Demand = [
    [50,150,250],
    [20,110,250],
    [200,225,500]]

Sell = [60,40,10]

m = Model("Dakota")

Y = {(r): m.addVar() for r in R}
X = {(p,s): m.addVar() for p in P for s in S}

# objective

m.setObjective(quicksum(Prob[s] * quicksum(Sell[p] * X[p,s] for p in P) for s in S) - quicksum(Cost[r] * Y[r] for r in R), GRB.MAXIMIZE)

ResourceLimit = {   (s,r):
                    m.addConstr(quicksum(Input[r][p] * X[p,s] for p in P) <= Y[r]) for s in S for r in R}

DemandLimit = {(p,s): m.addConstr(X[p,s] <= Demand[p][s]) for p in P for s in S}

m.optimize()

print("\n\n")
print("Objective Value: " + str(m.objVal))
