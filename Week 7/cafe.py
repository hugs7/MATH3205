from gurobipy import Model, quicksum, GRB

P = range(100, 250, 5)
T = range(300, 450, 5)

m = Model("Cafe")

X = {p: m.addVar(vtype=GRB.BINARY) for p in P}
Y = {(p, t): m.addVar(vtype=GRB.BINARY) for p in P for t in T}

m.setObjective(quicksum(X.values()), GRB.MINIMIZE)

Target = {m.addConstr(quicksum(p * Y[p, t] for p in P) == t) for t in T}
XY = {m.addConstr(Y[p, t] <= X[p]) for p in P for t in T}

m.optimize()

print(m.objVal)

for t in T:
    print(t, [p for p in P if Y[p, t].x > 0.9])
