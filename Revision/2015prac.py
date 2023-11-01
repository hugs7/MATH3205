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

# Squares that have to move
SOut = {(i, j) for i in N for j in N if Data[i][j] > 0}

# All squares (to move to)
SIn = {(i, j) for i in N for j in N}

T = range(len(SOut))
maxT = T[-1] + 1


def MoveTo(s):
    # Return the squares we can move to from square s
    retList = set()
    i, j = s
    d = Data[i][j]
    for di in [-d, 0, d]:
        for dj in [-d, 0, d]:
            if (di != 0 or dj != 0) and (i + di, j + dj) in SIn:
                retList.add((i + di, j + dj))
    return retList


# Set this to True to test the PartB code, or false for the PartD code
PartB = False

if PartB:
    m = Model("ZNumbers")

    X = {
        (s, s_prime, t): m.addVar(vtype=GRB.BINARY)
        for s in SOut
        for s_prime in SIn
        for t in T
    }
    print("Variables Defined")

    # Constraints
    # Must move each square exactly once
    MoveOnce = {
        s: m.addConstr(quicksum(X[s, s_prime, t] for s_prime in SIn for t in T) == 1)
        for s in SOut
    }

    # Can't move square to square already occupied
    Occupied = {
        (s, t): m.addConstr(
            quicksum(X[s_prime, s, t] for s_prime in SOut if s_prime != s)
            <= quicksum(
                X[s, s_prime, t_prime]
                for s_prime in SIn
                if s_prime != s
                for t_prime in T
                if t_prime < t
            )
            - quicksum(
                X[s_prime, s, t_prime]
                for s_prime in SOut
                if s_prime != s
                for t_prime in T
                if t_prime < t
            )
        )
        for s in SOut
        for t in T
    }

    Occupied_Empty = {
        (s, t): m.addConstr(
            quicksum(X[s_prime, s, t] for s_prime in SOut if s_prime != s)
            <= 1
            - quicksum(
                X[s_prime, s, t_prime]
                for s_prime in SOut
                if s_prime != s
                for t_prime in T
                if t_prime < t
            )
        )
        for s in SIn
        if s not in SOut
        for t in T
    }

    # Move square by distance
    Distance = {
        s: m.addConstr(
            quicksum(
                X[s, s_prime, t]
                for s_prime in SIn
                if s_prime not in MoveTo(s)
                for t in T
            )
            == 0
        )
        for s in SOut
    }

    # One move per turn
    OneMove = {
        t: m.addConstr(quicksum(X[s, s_prime, t] for s in SOut for s_prime in SIn) == 1)
        for t in T
    }

    # No objective
    print("Constraints Defined")
    # optimise
    m.optimize()
    # print original board
    for i in N:
        for j in N:
            if Data[i][j] != 0:
                print(Data[i][j], end="")
            else:
                print(" ", end="")
        print()
    print("-----")
    print("solution:")
    for t in T:
        print("Turn ", t)
        for i in N:
            for j in N:
                printed = False
                for s in SOut:
                    if (
                        sum(X[s, (i, j), t_prime].x for t_prime in T if t_prime <= t)
                        > 0.5
                    ):
                        i_prime, j_prime = s
                        print(Data[i_prime][j_prime], end="")
                        printed = True
                if not printed:
                    if Data[i][j] != 0:
                        print(Data[i][j], end="")
                    else:
                        print(" ", end="")

            print()
        print("----")

    for t in T:
        print("Turn ", t)
        for s in SOut:
            for s_prime in SIn:
                if X[s, s_prime, t].x > 0.5:
                    print(s, " -> ", s_prime)
else:
    # Put the Part D code here
    BMP = Model("ZNumbers Master")

    # Variables

    X = {(s, s_prime): BMP.addVar(vtype=GRB.BINARY) for s in SOut for s_prime in SIn}

    # Constraints

    MoveOnce = {
        s: BMP.addConstr(quicksum(X[s, s_prime] for s_prime in SIn) == 1) for s in SOut
    }

    MoveByDistance = {
        BMP.addConstr(
            quicksum(X[s, s_prime] for s_prime in SIn if s_prime not in MoveTo(s)) == 0
        )
        for s in SOut
    }

    # No objectvie

    # Define callback
    def callback(model, where):
        if where != GRB.Callback.MIPSOL:
            return

        print("Callback")

        # Data
        # Get solution of X from master problem
        XV = model.cbGetSolution(X)

        # Cycles
        STo = {}
        for k in XV:
            if XV[k] > 0.5:
                STo[k[0]] = k[1]
        for s in SOut:
            LoopSet = set()
            upto = s
            while upto in STo and upto not in LoopSet:
                LoopSet.add(upto)
                upto = STo[upto]
            if upto not in LoopSet:
                continue
            print("Cycle: ", LoopSet)
            model.cbLazy(
                quicksum(X[s1, s2] for s1 in LoopSet for s2 in LoopSet if (s1, s2) in X)
                <= len(LoopSet) - 1
            )
            for upto in LoopSet:
                del STo[upto]

    BMP.setParam("LazyConstraints", 1)
    BMP.optimize(callback)

    for s in SOut:
        for s_prime in SIn:
            if X[s, s_prime].x > 0.5:
                print(s, " -> ", s_prime)

    print("-------------------")
    # Sort order of moves in second stage

    # Define subproblem
    BSP = Model("ZNumbers SubProblem")

    # Determine moved to squares are on for square s (should be just 1)
    MovedTo = {s: {s_prime for s_prime in SIn if X[s, s_prime].x > 0.5} for s in SOut}
    for s in SOut:
        print(s, " -> ", MovedTo[s])

    # Variables
    Y = {(s, t): BSP.addVar(vtype=GRB.BINARY) for s in SOut for t in T}
    # 1 when square s is moved

    # Constraints

    # Move once per turn
    OncePerTurn = {t: BSP.addConstr(quicksum(Y[s, t] for s in SOut) == 1) for t in T}

    # Move to free spot
    FreeSpot = {
        (s, t): BSP.addConstr(
            quicksum(Y[s_prime, t] for s_prime in SOut if s in MovedTo[s_prime])
            <= 1
            - quicksum(Y[s, t_prime] for t_prime in T if t_prime > t)
            - quicksum(
                Y[s_prime, t_prime]
                for s_prime in SOut
                if s in MovedTo[s_prime]
                for t_prime in T
                if t_prime < t
            )
        )
        for s in SOut
        for t in T
    }

    # No subproblem objective

    # Optimise subproblem
    BSP.setParam("OutputFlag", 0)
    BSP.optimize()

    if BSP.status == GRB.INFEASIBLE:
        print("Infeasible subproblem")

        exit()
    else:
        print("feasible subproblem")
        for t in T:
            print("Turn ", t)
            for s in SOut:
                if Y[s, t].x > 0.5:
                    print(s, " -> ", MovedTo[s])
