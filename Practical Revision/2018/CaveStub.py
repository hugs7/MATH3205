from gurobipy import GRB, quicksum, Model

# Define some helper functions


def inBoard(s):
    i, j = None, None
    try:
        i, j = s
    except:
        print("S", s)

    return i in N and j in N


def moveSquare(square, direction, distance):
    i, j = square
    return (i + distance * direction[0], j + distance * direction[1])


Directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
# 0 = down, 1 = right, 2 = up, 3 = left

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

n = len(Data)
N = range(n)

# Sets

Seeds = {(i, j): int(Data[i][j]) for i in N for j in N if Data[i][j] != " "}
Squares = {(i, j) for i in N for j in N}
# Set of distances for square s in direction d such that the resulting square is still in the board
I = {
    (s, d): set(i for i in N if inBoard(moveSquare(s, d, i)))
    for s in Squares
    for d in Directions
}

m = Model("Cave")

# Variables

X = {s: m.addVar(vtype=GRB.BINARY) for s in Squares}
Y = {
    (p, d, i): m.addVar(vtype=GRB.BINARY)
    for p in Seeds.keys()
    for d in Directions
    for i in I[p, d]
}

# Constraints

for d in Directions:
    print(f"Direction {d}: {I[(0, 0), d]}")

# Square can't be shaded if it is a seed
CantShade = {p: m.addConstr(X[p] == 0) for p in Seeds.keys()}
print(I[(0, 1), (1, 0)])

# Sum of y over D + 1 equqls number
EqualOpen = {
    p: m.addConstr(
        quicksum(i * Y[p, d, i] for d in Directions for i in I[p, d]) == Seeds[p] - 1
    )
    for p in list(Seeds.keys())
}

# 1 Y on per direction if at least 1 square in that direction is on the board
OneY = {
    (p, d): m.addConstr(quicksum(Y[p, d, i] for i in I[p, d]) == 1)
    for p in Seeds.keys()
    for d in Directions
    if len(I[p, d]) > 0
}

# If Y is on, then the square after it in that direction is on if that square is on the board
TurnXOn = {
    (p, d, i): m.addConstr(Y[p, d, i] <= X[moveSquare(p, d, i + 1)])
    for p in list(Seeds.keys())
    for d in Directions
    for i in I[p, d]
    if inBoard(moveSquare(p, d, i + 1))
}

# All Xs before Y bounded above by sum of Y
BoundX = {
    (p, d, i): m.addConstr(
        quicksum(Y[p, d, i_prime] for i_prime in I[p, d] if i_prime < i)
        >= X[moveSquare(p, d, i)]
    )
    for p in Seeds.keys()
    for d in Directions
    for i in I[p, d]
}


m.optimize()

if m.status == GRB.INFEASIBLE:
    print("No solution")
    exit(1)

# print board
g = 3
for i in N:
    for j in N:
        if X[(i, j)].x > 0.9:
            print("▒" * g, end="")
        elif (i, j) in Seeds.keys():
            print(f"|{Seeds[(i, j)]}|", end="")
        else:
            print("| |", end="")

    print()

for p in Seeds.keys():
    print(p, Seeds[p])
    for d in Directions:
        for i in I[p, d]:
            if Y[p, d, i].x > 0.9:
                print(f"Y[{p}, {d}, {i}] = 1")
