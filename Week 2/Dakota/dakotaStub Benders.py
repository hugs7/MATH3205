from gurobipy import Model, quicksum, GRB

EPS = 1e-6

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

BMP = Model("Dakota Master Problem")

Y = {(r): BMP.addVar() for r in R}    # Qty of each resource we have available
Theta = {s: BMP.addVar(lb=-sum(Demand[p][s]*Sell[p] for p in P)) for s in S} # Solution for each subproblem

BMP.setObjective(quicksum(Cost[r]*Y[r] for r in R) + quicksum(Theta[s] * Prob[s] for s in S), GRB.MINIMIZE)

for k in range(40):
    cutsAdded = 0
    BMP.optimize()
    BMP.setParam('OutputFlag', 0)

    print("-"*80)

    print([Y[k].x for k in Y])
    print([Theta[k].x for k in Theta])

    print("\n")

    print("Master Objective = ", BMP.objVal)

    print("Y=", [Y[r].x for r in R])

    print("\n")
    for s in S:
        BSP = Model("Bender's Subproblem")
        BSP.setParam('OutputFlag', 0)
        X = {p: BSP.addVar() for p in P}

        BSP.setObjective(- quicksum(X[p] * Sell[p] for p in P))
        DemandLimit = {p: BSP.addConstr(X[p] <= Demand[p][s]) for p in P}
        ResourceLimit = {r: BSP.addConstr(quicksum(Input[r][p] * X[p] for p in P) <= Y[r].x) for r in R}

        BSP.optimize()

        print("BSP Scenario" + str(s))
        print(" " * 5 + "Theta, BSP Obj Val", Theta[s].x, BSP.objVal)
        print(" " * 5 + "Subproblem Answers", [X[p].x for p in P])


        if BSP.objVal > Theta[s].x + EPS:
            cutsAdded += 1
            BMP.addConstr(Theta[s] >= quicksum(ResourceLimit[r].pi * Y[r] for r in R) + 
                        quicksum(DemandLimit[p].pi * Demand[p][s] for p in P))
        elif BSP.objVal < Theta[s].x - EPS:
            print("######## Bad Theta", s, Theta[s].x, BSP.objVal)

    if cutsAdded == 0:
        print("Stopped at ", k)
        break


print("Global Objective: " + str(-BMP.objVal))