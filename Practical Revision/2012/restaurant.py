from gurobipy import GRB, quicksum, Model

# Sets
Items = range(200, 355, 5)
Amounts = range(500, 805, 5)


# Model

m = Model("Restaurant")

# Variables

X = {(a, i): m.addVar(vtype=GRB.BINARY) for a in Amounts for i in Items}
Y = {i: m.addVar(vtype=GRB.BINARY) for i in Items}

# Constraints
# Can't have item in any orders if it's not on the menu
OnMenu = {
    i: m.addConstr(quicksum(X[a, i] for a in Amounts) <= len(Amounts) * Y[i])
    for i in Items
}

# Each order adds to it's total
AddToTotal = {
    a: m.addConstr(quicksum(X[a, i] * i for i in Items) == a) for a in Amounts
}

# Objective

# Minimise items on menu
m.setObjective(quicksum(Y[i] for i in Items), GRB.MINIMIZE)

m.optimize()

# Print menu
print(f"\n\nMenu contains {int(sum(Y[i].x for i in Items))} items:")
for i in Items:
    if Y[i].x > 0.9:
        print(f"Item ${i} on menu")

print("---")
# Print orders
print("Orders")
for a in Amounts:
    print(f"Order ${a} contains items: ${[i for i in Items if X[a, i].x > 0.9]}")
