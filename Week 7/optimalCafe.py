from gurobipy import Model, quicksum, GRB

P = range(150, 355, 5)
T = range(500, 805, 5)

# Tuples of prices that hit target
B = {t: [] for t in T}

# collections of items
upto = 1
Comb = {upto: [(p, (p,)) for p in P]}

while len(Comb[upto]) > 0:
    tList = []
    print(upto, len(Comb[upto]))
    for t, ptup in Comb[upto]:
        if t in B:
            B[t].append(ptup)
        for p in P:
            if p > ptup[-1] and t + p <= T[-1]:
                tList.append((t + p, ptup + (p,)))

    upto += 1
    Comb[upto] = tList

m = Model("Cafe")

X = {p: m.addVar(vtype=GRB.BINARY) for p in P}
Z = {(b, t): m.addVar() for t in T for b in B[t]}

m.setObjective(quicksum(X.values()), GRB.MINIMIZE)

ZX = {
    (p, t): m.addConstr(quicksum(Z[b, t] for b in B[t] if p in b) <= X[p])
    for p in P
    for t in T
}

OnePerTarget = {t: m.addConstr(quicksum(Z[b, t] for b in B[t]) == 1) for t in T}

for p in P:
    X[p].BranchPriority = p

m.optimize()

print(m.objVal)

# for t in T:
#     for b in B[t]:
#         if Z[b, t].x > 0.9:
#             print(t, b)
