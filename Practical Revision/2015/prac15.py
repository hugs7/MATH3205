# Solution for MATH4202 2015 Prac exam

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

Data = Data2

# The size of the square
N = range(len(Data))

SOut = [(i, j) for i in N for j in N if Data[i][j] > 0]
SIn = [(i, j) for i in N for j in N]

T = range(len(SOut))
maxT = T[-1] + 1


def MoveTo(s):
    # Return the squares we can move to from the square at s
    retList = []
    i, j = s
    d = Data[i][j]
    for di in [-d, 0, d]:
        for dj in [-d, 0, d]:
            if (
                i + di >= 0
                and i + di <= N[-1]
                and j + dj >= 0
                and j + dj <= N[-1]
                and (di != 0 or dj != 0)
            ):
                retList.append((i + di, j + dj))
    return retList


PartB = True

if PartB:
    m = Model("ZNumber")
    X = {
        (s1, s2, t): m.addVar(vtype=GRB.BINARY)
        for s1 in SOut
        for s2 in MoveTo(s1)
        for t in T
    }

    m.update()

    # Move away from every square
    [m.addConstr(quicksum(X[k] for k in X if k[0] == s) == 1) for s in SOut]
    # At most one move into every square
    [m.addConstr(quicksum(X[k] for k in X if k[1] == s) <= 1) for s in SIn]
    # One move in every time period
    [m.addConstr(quicksum(X[k] for k in X if k[2] == t) == 1) for t in T]
    # Must move out of a square before we move into it
    [
        m.addConstr(
            quicksum((maxT - k[2]) * X[k] for k in X if k[0] == s)
            >= quicksum((maxT - k[2]) * X[k] for k in X if k[1] == s)
        )
        for s in SOut
    ]

    m.optimize()
    for t in T:
        for k in X:
            if k[2] == t and X[k].x > 0.9:
                print(k[0], k[1])
else:
    m = Model("ZNumber")
    X = {(s1, s2): m.addVar(vtype=GRB.BINARY) for s1 in SOut for s2 in MoveTo(s1)}
    m.update()
    m.setParam("LazyConstraints", 1)
    kList = [k for k in X]
    XList = [X[k] for k in kList]
    IR = range(len(XList))

    def CallBack(model, where):
        if where == GRB.Callback.MIPSOL:
            XVal = model.cbGetSolution(XList)
            Done = {s: False for s in SOut}
            for s in SOut:
                if not Done[s]:
                    p = s
                    TList = []
                    while p in SOut and not Done[p]:
                        TList.append(p)
                        Done[p] = True
                        p = max((XVal[i], kList[i][1]) for i in IR if kList[i][0] == p)[
                            1
                        ]
                    if p == s:
                        model.cbLazy(
                            quicksum(
                                X[s1, s2]
                                for s1 in TList
                                for s2 in TList
                                if (s1, s2) in X
                            )
                            <= len(TList) - 1
                        )
                        print("Cycle", TList)

    # Move away from every square
    [m.addConstr(quicksum(X[k] for k in X if k[0] == s) == 1) for s in SOut]
    # At most one move into every square
    [m.addConstr(quicksum(X[k] for k in X if k[1] == s) <= 1) for s in SIn]

    m.optimize(CallBack)

    DoneList = []
    for s in SIn:
        if s not in SOut:
            while True:
                for k in X:
                    if X[k].x > 0.9 and k[1] == s:
                        print(k)
                        DoneList.append(k[0])
                        s = k[0]
                        break
                else:
                    break
    DoneList.sort()
    if DoneList != SOut:
        print(DoneList)
        print(SOut)
