# Stub for MATH4202 2015 Prac exam

from gurobipy import GRB, quicksum, Model

# The data for the squares
Data1 = [
    [0, 0, 0, 0, 0, 0],
    [3, 2, 3, 2, 2, 2],
    [0, 0, 2, 3, 2, 2],
    [2, 0, 2, 2, 0, 0],
    [0, 2, 3, 0, 2, 2],
    [2, 3, 0, 2, 0, 4],
]

Data2 = [
    [3, 2, 2, 3, 2, 1, 3, 2, 2, 0, 2, 0],
    [2, 3, 2, 3, 2, 0, 2, 3, 2, 3, 2, 3],
    [0, 1, 3, 1, 2, 2, 0, 1, 3, 1, 2, 2],
    [1, 1, 0, 1, 3, 1, 1, 1, 0, 3, 0, 1],
    [2, 2, 1, 3, 3, 1, 2, 2, 1, 3, 3, 1],
    [3, 2, 1, 1, 2, 2, 3, 2, 1, 1, 2, 2],
    [3, 2, 2, 1, 2, 0, 3, 2, 2, 0, 2, 0],
    [2, 3, 2, 3, 2, 2, 2, 3, 2, 3, 2, 0],
    [0, 1, 3, 1, 2, 2, 0, 1, 3, 1, 2, 2],
    [1, 1, 0, 0, 2, 1, 1, 1, 1, 0, 2, 1],
    [2, 2, 1, 3, 3, 1, 2, 2, 1, 3, 3, 1],
    [3, 2, 1, 1, 2, 2, 3, 2, 1, 1, 2, 2],
]

# Change this next line to test with Data1 or Data2
Data = Data2

# The size of the square
N = range(len(Data))

SOut = {(i, j) for i in N for j in N if Data[i][j] > 0}
SIn = {(i, j) for i in N for j in N}

T = range(len(SOut))
maxT = T[-1] + 1


def _MoveTo(s):
    # Return the squares we can move to from square s
    retList = set()
    i, j = s
    d = Data[i][j]
    for di in [-d, 0, d]:
        for dj in [-d, 0, d]:
            if (di != 0 or dj != 0) and (i + di, j + dj) in SIn:
                retList.add((i + di, j + dj))
    return retList


MoveTo = {s: _MoveTo(s) for s in SOut}

# Set this to True to test the PartB code, or false for the PartD code
PartB = False

m = Model()
if PartB:
    # Put the Part B code here.
    X = {
        (s1, s2, t): m.addVar(vtype=GRB.BINARY)
        for s1 in SOut
        for s2 in MoveTo[s1]
        for t in T
    }
    MoveOut = {
        s1: m.addConstr(quicksum(X[s1, s2, t] for s2 in MoveTo[s1] for t in T) == 1)
        for s1 in SOut
    }
    OnePerTurn = {
        t: m.addConstr(quicksum(X[s1, s2, t] for s1 in SOut for s2 in MoveTo[s1]) == 1)
        for t in T
    }
    InOnce = {s: m.addConstr(quicksum(X[k] for k in X if k[1] == s) <= 1) for s in SIn}
    print("In Once done")
    # Only into a square in time t if moved out beforehand
    OutBeforeIn = {
        (t, s): m.addConstr(
            quicksum(X[s2, s, t] for s2 in SOut if (s2, s, t) in X)
            <= quicksum(X[s, s2, td] for s2 in MoveTo[s] for td in T[:t])
        )
        for t in T
        for s in SOut
    }
    print("Out Before in done")
    m.optimize()
    for t in T:
        for s1 in SOut:
            for s2 in MoveTo[s1]:
                if X[s1, s2, t].x > 0.9:
                    print(s1, s2, t)
else:

    def Callback(model, where):
        if where == GRB.Callback.MIPSOL:
            XV = model.cbGetSolution(X)
            STo = {}
            # Store where each square goes to
            for k in XV:
                if XV[k] > 0.9:
                    STo[k[0]] = k[1]
            # Loop over each out square
            for s in SOut:
                # Run down chain of where it goes to
                LoopSet = set()
                upto = s
                # Stop if we find a loop or don't go anywhere
                while upto in STo and upto not in LoopSet:
                    LoopSet.add(upto)
                    upto = STo[s]
                if upto in LoopSet:
                    # We have found a loop with LoopSet
                    print("Loop:", LoopSet)
                    model.cbLazy(
                        quicksum(
                            X[s1, s2]
                            for s1 in LoopSet
                            for s2 in LoopSet
                            if (s1, s2) in X
                        )
                        <= len(LoopSet) - 1
                    )
                # Make sure we don't find it again
                for upto in LoopSet:
                    del STo[upto]

    # Put the Part D code here
    X = {(s1, s2): m.addVar(vtype=GRB.BINARY) for s1 in SOut for s2 in MoveTo[s1]}
    MoveOut = {
        s1: m.addConstr(quicksum(X[s1, s2] for s2 in MoveTo[s1]) == 1) for s1 in SOut
    }
    InOnce = {s: m.addConstr(quicksum(X[k] for k in X if k[1] == s) <= 1) for s in SIn}
    m.setParam("LazyConstraints", 1)
    m.optimize(Callback)
    for k in sorted(X.keys()):
        if X[k].x > 0.9:
            print(k)
