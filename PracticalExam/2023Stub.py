from gurobipy import GRB, Model, quicksum

# Edges are (0,1,2,3) = (top, right, bottom, left)
# Top left of board is (0,0)
# Bottom right of board is (11,11) for this data

# The pieces are labelled for the two edges they connect
# (0,1), (0,2), (0,3), (1,2), (1,3), (2,3)


def Neighbours(s):
    i, j = s
    tList = []
    if i > 0:
        tList.append((i - 1, j))
    if i < NColumns - 1:
        tList.append((i + 1, j))
    if j > 0:
        tList.append((i, j - 1))
    if j < NRows - 1:
        tList.append((i, j + 1))
    return tList


PathPositions = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

# # Lookup of which pieces can join to which other pieces
# JoinLookup = {
#     (0, 1): [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)],
# }

PDraw = {
    (0, 1): ("+#+", "|##", "+-+"),
    (0, 2): ("+#+", "|#|", "+#+"),
    (0, 3): ("+#+", "##|", "+-+"),
    (1, 2): ("+-+", "|##", "+#+"),
    (1, 3): ("+-+", "###", "+-+"),
    (2, 3): ("+-+", "##|", "+#+"),
}


ColSum = [9, 6, 9, 5, 6, 4, 4, 3, 6, 5, 5, 6]
RowSum = [6, 7, 6, 11, 10, 9, 5, 5, 2, 2, 2, 3]
NColumns = len(ColSum)
NRows = len(RowSum)


I = range(len(RowSum))
J = range(len(ColSum))

# These are the initial squares
Init = {
    (2, 5): (0, 3),
    (2, 7): (0, 3),
    (3, 3): (1, 3),
    (3, 5): (1, 2),
    (3, 8): (0, 2),
    (3, 10): (2, 3),
    (4, 3): (1, 3),
    (5, 0): (1, 2),
    (6, 2): (1, 3),
    (6, 4): (0, 2),
    (9, 2): (0, 2),
    (11, 0): (1, 2),
    (10, 0): (0, 3),
}

# These are the ends (part of the initial squares)
Ends = [(10, 0), (11, 0)]


###

# Sets
# Squares
S = [(i, j) for i in I for j in J]
# Set of starting squares - only on borders
StartingSquares = [
    (i, j)
    for i in I
    for j in J
    if (i == 0 or j == 0 or i == NRows - 1 or j == NColumns - 1) and (i != 0 and j != 0)
]

# Neighbours of square s
Neighs = {s: Neighbours(s) for s in S}

# Set of possible paths

PathPositions = []
PathPieces = []


def growPath(
    subPathPositions,
    subPathPieces,
    tailPosition,
    tailSide,
    lengthRemaining,
    neighbours,
    usedTilePos,
):
    # print(word, endPosition, lengthRemaining)
    if lengthRemaining == 0:
        print("Path found", subPathPositions)
        # print("Path found", subPathPieces)
        # Convert list of positions to string
        # Add to list of generated words
        # if tailPosition in StartingSquares:
        PathPositions.append(tuple(subPathPositions))
        PathPieces.append(tuple(subPathPieces))
    else:
        if len(subPathPositions) == 0:
            # loop over the starting squares
            startingTile = Init[Ends[0]]
            tilePos = Ends[0]
            for startingSquarePos in StartingSquares:
                print("Starting square", startingSquarePos)
                startingTile = Init[Ends[0]]
                # print("startingTile", startingTile)
                # Add the tile to the list of pieces
                newSubPathPieces = subPathPieces + [startingTile]

                # Add position to list
                newSubPathPositions = subPathPositions + [startingSquarePos]

                if startingSquarePos[0] == 0 or startingSquarePos[0] == NRows - 1:
                    newTailSide = startingTile[1]

                if startingSquarePos[1] == 3 or startingSquarePos[1] == NColumns - 1:
                    newTailSide = startingTile[0]
                growPath(
                    newSubPathPositions,
                    newSubPathPieces,
                    startingSquarePos,
                    newTailSide,
                    lengthRemaining - 1,
                    neighbours,
                    [tilePos] + usedTilePos,
                )

        else:
            for childPosition in neighbours[tailPosition]:
                if childPosition in subPathPositions:
                    # can't use this neighbour as position is already used
                    continue

                # Loop over remaining tiles
                for tilePos, tile in Init.items():
                    if tilePos in usedTilePos:
                        # tile already used
                        continue

                    setTailSide = 0
                    if tailSide == 0:
                        if tile[0] == 0:
                            newTailSide = tile[1]
                            setTailSide += 1
                        if tile[1] == 0:
                            newTailSide = tile[0]
                            setTailSide += 1
                    if tailSide == 1:
                        if tile[0] == 1:
                            newTailSide = tile[1]
                            setTailSide += 1
                        if tile[1] == 1:
                            newTailSide = tile[0]
                            setTailSide += 1
                    if tailSide == 2:
                        if tile[0] == 2:
                            newTailSide = tile[1]
                            setTailSide += 1
                        if tile[1] == 2:
                            newTailSide = tile[0]
                            setTailSide += 1
                    if tailSide == 3:
                        if tile[0] == 3:
                            newTailSide = tile[1]
                            setTailSide += 1
                        if tile[1] == 3:
                            newTailSide = tile[0]
                            setTailSide += 1
                    if setTailSide == 0:
                        # tile doesn't match the tail
                        continue
                    # Tile available

                    # Add the neighbour to the list of positions
                    newSubPathPositions = subPathPositions + [childPosition]

                    # Add the tile to the list of pieces
                    newSubPathPieces = subPathPieces + [tile]
                    # print(newSubPathPieces)
                    # print(
                    #     newSubPathPieces,
                    #     "\n",
                    #     newSubPathPositions,
                    #     "\n",
                    #     lengthRemaining - 1,
                    #     "\n---",
                    # )
                    # can use this neighbour
                    # Recurse
                    growPath(
                        newSubPathPositions,
                        newSubPathPieces,
                        childPosition,
                        newTailSide,
                        lengthRemaining - 1,
                        neighbours,
                        [tilePos] + usedTilePos,
                    )


numPieces = len(Init)
print("Number of pieces", numPieces)
growPath([], [], None, None, numPieces, Neighs, [])

print("Number of possible paths", len(PathPositions))
for i in range(5):
    print(list(PathPositions)[i])

###


def Draw(pDict):
    # Build the blank board
    Board = []
    Sep = "+"
    Line = "|"
    for j in J:
        Sep += "-+"
        Line += " |"
    Board.append(Sep)
    for i in I:
        Board.append(Line)
        Board.append(Sep)
    # Now go through and over write the blank board with the pieces used
    for i, j in pDict:
        draw = PDraw[pDict[i, j]]
        for ii in range(3):
            for jj in range(3):
                if draw[ii][jj] == "#":
                    Board[2 * i + ii] = (
                        Board[2 * i + ii][: 2 * j + jj]
                        + "#"
                        + Board[2 * i + ii][2 * j + jj + 1 :]
                    )
    for s in Board:
        print(s)


Draw(Init)


m = Model("Tracks")


# Variables

X = {p: m.addVar(vtype=GRB.BINARY) for p in PathPositions}

# Constraints

OnePath = m.addConstr(quicksum(X[p] for p in PathPositions) == 1)

RowCount = {
    i: m.addConstr(quicksum(X[p] for p in PathPositions if i in p[0]) == RowSum[i])
    for i in I
}
ColCount = {
    j: m.addConstr(quicksum(X[p] for p in PathPositions if j in p[1]) == ColSum[j])
    for j in J
}

# Optimize

m.optimize()
# Determine which path was chosen
chosenPath = None
chosenPathPieces = None
for p in PathPositions:
    if X[p].x > 0.9:
        chosenPath = p
        chosenPathPieces = PathPieces[PathPositions.index(p)]
        break

print("Chosen path", chosenPath)
print("Chosen path pieces", chosenPathPieces)

# generate lookup table of positions to pieces
PDict = {}
for p in chosenPath:
    PDict[p[0]] = p[1]
