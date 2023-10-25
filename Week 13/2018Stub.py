from typing import Dict, Tuple
from gurobipy import Model, quicksum, GRB
import heapq


Data = [
    "6   6    4",
    "     6    ",
    "  3    5  ",
    "   7  9   ",
    " 5  3    5",
    "5    5  2 ",
    "   2  4   ",
    "  7    4  ",
    "    2     ",
    "5    6   6",
]

D = [(0, 1), (0, -1), (1, 0), (-1, 0)]
n = len(Data)
N = range(n)

# Set of seeds

Board = set((i, j) for i in N for j in N)


def Move(s, k, d):
    return (s[0] + k * d[0], s[1] + k * d[1])


n = len(Data)
N = range(n)

Seeds = {(i, j): int(Data[i][j]) for i in N for j in N if Data[i][j] != " "}

m = Model("Cave")


# Variables

X = {(s): m.addVar(vtype=GRB.BINARY) for s in Board}

Y = {
    (s, k, d): m.addVar(vtype=GRB.BINARY)
    for s in Seeds
    for k in range(Seeds[s])
    for d in D
    if Move(s, k, d) in Board
}

# Constraints

OneEachDirection = {
    (s, d): m.addConstr(
        quicksum(Y[s, k, d] for k in range(Seeds[s]) if (s, k, d) in Y) == 1
    )
    for s in Seeds
    for d in D
}

CorrectTotal = {
    s: m.addConstr(
        quicksum(k * Y[s, k, d] for k in range(Seeds[s]) for d in D if (s, k, d) in Y)
        == Seeds[s] - 1
    )
    for s in Seeds
}

YXOff = {
    (s, k, d): m.addConstr(
        quicksum(Y[s, kd, d] for kd in range(k, Seeds[s]) if (s, kd, d) in Y)
        <= 1 - X[Move(s, k, d)]
    )
    for (s, k, d) in Y
}

YOn = {
    (s, k, d): m.addConstr(Y[s, k, d] <= X[Move(s, k + 1, d)])
    for (s, k, d) in Y
    if Move(s, k + 1, d) in Board
}


def Callback(model, where):
    if where != GRB.Callback.MIPSOL:
        return

    print("\n\n\n\n\n")
    # find all the connected regions of walls as a set of sets using a breadth first search algorithm
    # start with the first seed

    # Get solution

    XV = model.cbGetSolution(X)
    Walls = [s for s in Board if XV[s] > 0.5]
    print("Walls", Walls)
    Regions = []

    allVisited = []

    while len(allVisited) < len(Walls):
        frontier = []

        while len(allVisited) < len(Walls):
            frontier = []
            visitedWalls = set()

            region = []

            # Choose a wall which doesn't appear in allVisited
            wall = next(w for w in Walls if w not in allVisited)

            # Add the wall to the frontier
            heapq.heappush(frontier, wall)

            while True:
                print(len(frontier), len(visitedWalls))
                try:
                    square = heapq.heappop(frontier)
                except IndexError:  # Queue is empty
                    break

                if square in visitedWalls:
                    # Check if we've been to this state before and skip if we have
                    continue

                visitedWalls.add(square)
                region.append(square)

                for direction in D:
                    child = Move(square, 1, direction)
                    if not (child in Board and XV[child] > 0.5):
                        # We can't move here
                        continue

                    print("Child", child, "Square", square, "Direction", direction)

                    if child not in region:
                        region.append(child)

                    if child not in visitedWalls and child not in frontier:
                        # If we haven't seenn this child before, add to the frontier
                        heapq.heappush(frontier, child)  # Add to frontier
                        # Add to visited

            Regions.append(region)
            for square in region:
                allVisited.append(square)

        print("regions", Regions)


m.optimize(Callback)

for i in range(n):
    for j in range(n):
        if Data[i][j] != " ":
            # Print number
            print(Data[i][j], end="")
        elif X[i, j].X > 0.5:
            # print block
            print("█", end="")
        else:
            print("_", end="")
    print()
