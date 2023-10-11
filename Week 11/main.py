# %%
from gurobipy import GRB, Model, quicksum
from toyinstance import ToyInstance
from largeinstance import LargeInstance
from shortestpaths import ShortestPaths
from plotpaths import PlotPaths

EPS = 1e-6

# Small instance
if False:
    pos, arcs, length = ToyInstance()
    ignition = 0
    delay = 50
    target = 28
    resources = {10: 2, 15: 3}

else:
    pos, arcs, length = LargeInstance()
    ignition = 23
    delay = 50
    target = 90
    resources = {10: 3, 20: 3, 30: 3}

nodes = range(len(pos))
times = list(resources.keys())
ignitions = [ignition]

# Get in and out arcs
inarcs = {n: [] for n in nodes}
outarcs = {n: [] for n in nodes}
for a in arcs:
    outarcs[a[0]].append((a[0], a[1]))
    inarcs[a[1]].append((a[0], a[1]))


BMP = Model("firefighting")

Z = {(n, t): BMP.addVar(vtype=GRB.BINARY) for n in nodes for t in times}

Theta = {n: BMP.addVar(vtype=GRB.BINARY) for n in nodes}

# At most one ignition
AtMostOne = {n: BMP.addConstr(quicksum(Z[n, t] for t in times) <= 1) for n in nodes}

AtMostAvail = {
    t: BMP.addConstr(quicksum(Z[n, t] for n in nodes) <= resources[t]) for t in times
}

BMP.setObjective(
    quicksum(Theta[n] for n in nodes),
    GRB.MINIMIZE,
)

for t in times:
    Z[ignition, t].ub = 0


def Callback(model, where):
    if where == GRB.Callback.MIPSOL:
        ZV = model.cbGetSolution(Z)
        ThetaV = model.cbGetSolution(Theta)

        incumbent = set(n for n in nodes for t in times if ZV[n, t] > 0.5)

        for n in nodes:
            if any(ZV[n, t] > 0.5 for t in times):
                tt = min(t for t in times if ZV[n, t] > 0.5)

                if arrival_time[n] < tt:
                    print(n, "INFEASIBLE")
                    model.cbLazy(
                        Z[n, tt]
                        <= quicksum(
                            Z[nn, t]
                            for nn in fire_path[n][:-1]
                            for t in times
                            if t <= arrival_time[nn] and ZV[nn, t] < 0.5
                        )
                    )

            if ThetaV[n] < 1 - EPS:
                # Model think node is safe

                if arrival_time[n] < target - EPS:
                    # But it should contribute none
                    model.cbLazy(
                        Theta[n]
                        > 1
                        - quicksum(
                            Z[nn, t]
                            for nn in fire_path[n][:-1]
                            for t in times
                            if t <= arrival_time[nn] and ZV[nn, t] < 0.5
                        )
                    )


BMP.setParam("OutputFlag", 1)
BMP.setParam("MIPGap", 0)
BMP.setParam("LazyConstraints", 1)
BMP.optimize(Callback)

solution = set(n for (n, t) in Z if Z[n, t].x > 0.5)

arrival_time, fire_path, pred = ShortestPaths(
    nodes, length, inarcs, outarcs, solution, ignitions, delay
)
PlotPaths(pos, arrival_time, pred, solution, ignitions, target, 10)
