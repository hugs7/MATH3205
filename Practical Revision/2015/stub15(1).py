# Stub for MATH4202 2015 Prac exam

from gurobipy import GRB, quicksum, Model
from colorama import init, Fore

# Initialize colorama
init()
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
Data = Data1

# The size of the square
N = range(len(Data))

SOut = [(i, j) for i in N for j in N if Data[i][j] > 0]
SIn = [(i, j) for i in N for j in N]

T = range(len(SOut))
maxT = T[-1] + 1


def MoveTo(s):
    # Return the squares we can move to from square s
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


# Set this to True to test the PartB code, or false for the PartD code
PartB = True

if PartB:
    # Put the Part B code here.
    m = Model("ZNumbers")

    # Sets
    # Set of candidate squares we can move to from (out of) square s
    C = {s: MoveTo(s) for s in SOut}

    # Variables
    X = {
        (sfrom, sto, t): m.addVar(vtype=GRB.BINARY)
        for sfrom in SOut
        for sto in C[sfrom]
        for t in T
    }

    # Constraints
    # Move once
    MoveOnce = {
        sfrom: m.addConstr(
            quicksum(X[sfrom, sto, t] for sto in C[sfrom] for t in T) == 1
        )
        for sfrom in SOut
    }

    MoveToVacant = {
        (sfrom, t): m.addConstr(
            quicksum(X[sfrom, sto, t] for sto in C[sfrom])
            <= 1
            - quicksum(
                X[sfrom_prime, sfrom, t_prime]
                for sfrom_prime in SOut
                if sfrom in C[sfrom_prime]
                for t_prime in T
                if t_prime < t
            )
            - quicksum(
                X[sfrom, sto_prime, t_prime]
                for sto_prime in C[sfrom]
                for t_prime in T
                if t_prime > t
            )
        )
        for sfrom in SOut
        for t in T
    }

    OneMovePerTurn = {
        t: m.addConstr(
            quicksum(X[sfrom, sto, t] for sfrom in SOut for sto in C[sfrom]) == 1
        )
        for t in T
    }

    # Optimize
    m.optimize()

    printGrid = True

    # Print output
    # Print base grid
    print("_" * (len(N) + 2))

    for i in N:
        print("|", end="")

        for j in N:
            if Data[i][j] > 0:
                print(Data[i][j], end="")
            else:
                print(" ", end="")
        print("|")
    print("-" * (len(N) + 2))

    print("----")
    for t in T:
        print("Turn", t)
        for sfrom in SOut:
            for sto in C[sfrom]:
                if X[sfrom, sto, t].x > 0.5:
                    print("Move ", sfrom, " to ", Fore.GREEN, sto, Fore.WHITE, sep="")

        # print grid
        if not printGrid:
            continue
        print("_" * (len(N) + 2))
        for i in N:
            print("|", end="")
            for j in N:
                square = (i, j)
                printMoved = False
                # loop over squares coming into square
                for sfrom in SOut:
                    # discard squares that cannot move to square
                    if square not in C[sfrom]:
                        continue

                    # If a tile is moved to square at or before time t, print the number of the square we moved from
                    if (
                        sum(
                            X[sfrom, square, t_prime].x for t_prime in T if t_prime <= t
                        )
                        > 0.5
                    ):
                        if X[sfrom, square, t].x > 0.5:
                            # Moved this turn
                            print(
                                Fore.GREEN + str(Data[sfrom[0]][sfrom[1]]) + Fore.WHITE,
                                end="",
                            )
                        else:
                            # Print the number of the square we moved from
                            print(
                                Fore.BLACK + str(Data[sfrom[0]][sfrom[1]]) + Fore.WHITE,
                                end="",
                            )

                        printMoved = True
                        break

                if not printMoved:
                    # No squares have been moved to this square at or before time t

                    # Check if this square is a starting tile

                    if Data[i][j] > 0:
                        # Check if we have moved FROM this square in the past
                        if (
                            sum(
                                X[square, sto, t_prime].x
                                for sto in C[square]
                                for t_prime in T
                                if t_prime <= t
                            )
                            > 0.5
                        ):
                            # Print blank
                            print(" ", end="")
                        else:
                            # check if moving this square in the next time step
                            if sum(X[square, sto, t + 1].x for sto in C[square]) > 0.5:
                                # Print the number of the square in red
                                print(Fore.RED + str(Data[i][j]) + Fore.WHITE, end="")
                            else:
                                # Print the number of the square
                                print(Data[i][j], end="")
                    else:
                        # Print blank
                        print(" ", end="")

            print("|")
        print("-" * (len(N) + 2))


else:
    # Put the Part D code here
    pass
