from gurobipy import quicksum, Model, GRB
import numpy as np
import csv
import os
from matplotlib import pyplot as plt

with open(os.path.join("Week 9", "CovMatrixNorm.csv"), "r") as f:
    reader = csv.reader(f, delimiter=",")
    temp1 = list(reader)

W = [[float(j) for j in i] for i in temp1]

NumAsset = 20

N = range(NumAsset)

# Small adjustment to make positive definite
for i in N:
    W[i][i] += 0.005

R = [
    1.071877684,
    1.075411639,
    1.10823578,
    1.07868473,
    1.103370352,
    1.312741894,
    1.117739229,
    1.058670271,
    1.178226399,
    1.063677793,
    1.133877788,
    1.128557584,
    1.010831389,
    1.096413424,
    1.120902431,
    1.01264185,
    1.061801832,
    1.131959114,
    1.119030185,
    1.115390706,
]

# Add the risk free asset
RiskFree = True
if RiskFree:
    R.append(1.05)
    for i in N:
        W[i].append(0.0)
    N = range(NumAsset + 1)
    W.append([0.0 for i in N])


Names = [
    "AMC",
    "ANZ",
    "BHP",
    "BXB",
    "CBA",
    "CSL",
    "GMG",
    "IAG",
    "MQG",
    "NAB",
    "NCM",
    "RIO",
    "SCG",
    "SUN",
    "TCL",
    "TLS",
    "WBC",
    "WES",
    "WOW",
    "WPL",
    "CSH",
]

S = range(10000)
np.random.seed(95)

# Generate a random sample
RS = np.random.multivariate_normal(R, W, len(S)).tolist()
alpha = 0.05

N = range(len(Names))

m = Model("CVAR")

# Create Gurobi variables
X = {i: m.addVar() for i in N}
Beta = {s: m.addVar() for s in S}
BetaMinus = {s: m.addVar() for s in S}
Var = m.addVar()
CVar = m.addVar()

# Constraints
investAll = m.addConstr(quicksum(X[i] for i in N) == 1)

SetBeta = {s: m.addConstr(Beta[s] == quicksum(RS[s][i] * X[i] for i in N)) for s in S}
SetBetaMinus = {s: m.addConstr(Beta[s] + BetaMinus[s] >= Var) for s in S}
SetCVar = m.addConstr(
    CVar == Var - 1 / (alpha * len(S)) * quicksum(BetaMinus[s] for s in S)
)

# Plotting
Ret = []
CV = []
LV = []
Obj = []
m.setParam("OutputFlag", 1)

for l in range(0, 101):
    Lambda = l * 0.01

    m.setObjective(
        (Lambda / len(S)) * quicksum(Beta[s] for s in S) + (1 - Lambda) * CVar,
        GRB.MAXIMIZE,
    )

    m.optimize()

    LV.append(Lambda)
    Ret.append(sum(Beta[s].x for s in S) / len(S))
    CV.append(CVar.x)
    Obj.append(m.objVal)

plt.plot(LV, Ret)
plt.plot(LV, CV)
plt.plot(LV, Obj)
plt.xlabel("Lambda")
plt.legend(["Return", "CVaR", "Objective"])
plt.ylabel("Value")
plt.show()


# Optimise

print(m.objVal)
