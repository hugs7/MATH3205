from typing import List, Tuple
from gurobipy import GRB, Model, quicksum

Size = 25
N = range(Size)

RowData = [
    [7, 3, 1, 1, 7],
    [
        1,
        1,
        2,
        2,
        1,
        1,
    ],
    [1, 3, 1, 3, 1, 1, 3, 1],
    [1, 3, 1, 1, 6, 1, 3, 1],
    [1, 3, 1, 5, 2, 1, 3, 1],
    [1, 1, 2, 1, 1],
    [7, 1, 1, 1, 1, 1, 7],
    [3, 3],
    [1, 2, 3, 1, 1, 3, 1, 1, 2],
    [1, 1, 3, 2, 1, 1],
    [4, 1, 4, 2, 1, 2],
    [1, 1, 1, 1, 1, 4, 1, 3],
    [2, 1, 1, 1, 2, 5],
    [3, 2, 2, 6, 3, 1],
    [1, 9, 1, 1, 2, 1],
    [2, 1, 2, 2, 3, 1],
    [3, 1, 1, 1, 1, 5, 1],
    [1, 2, 2, 5],
    [7, 1, 2, 1, 1, 1, 3],
    [1, 1, 2, 1, 2, 2, 1],
    [1, 3, 1, 4, 5, 1],
    [1, 3, 1, 3, 10, 2],
    [1, 3, 1, 1, 6, 6],
    [1, 1, 2, 1, 1, 2],
    [7, 2, 1, 2, 5],
]

ColData = [
    [7, 2, 1, 1, 7],
    [1, 1, 2, 2, 1, 1],
    [1, 3, 1, 3, 1, 3, 1, 3, 1],
    [1, 3, 1, 1, 5, 1, 3, 1],
    [1, 3, 1, 1, 4, 1, 3, 1],
    [1, 1, 1, 2, 1, 1],
    [7, 1, 1, 1, 1, 1, 7],
    [1, 1, 3],
    [2, 1, 2, 1, 8, 2, 1],
    [2, 2, 1, 2, 1, 1, 1, 2],
    [1, 7, 3, 2, 1],
    [1, 2, 3, 1, 1, 1, 1, 1],
    [4, 1, 1, 2, 6],
    [3, 3, 1, 1, 1, 3, 1],
    [1, 2, 5, 2, 2],
    [2, 2, 1, 1, 1, 1, 1, 2, 1],
    [1, 3, 3, 2, 1, 8, 1],
    [6, 2, 1],
    [7, 1, 4, 1, 1, 3],
    [1, 1, 1, 1, 4],
    [1, 3, 1, 3, 7, 1],
    [1, 3, 1, 1, 1, 2, 1, 1, 4],
    [1, 3, 1, 4, 3, 3],
    [1, 1, 2, 2, 2, 6, 1],
    [7, 1, 3, 2, 1, 1],
]

PreSet = [
    "-------------------------",
    "-------------------------",
    "-------------------------",
    "---XX-------XX-------X---",
    "-------------------------",
    "-------------------------",
    "-------------------------",
    "-------------------------",
    "------XX--X---XX--X------",
    "-------------------------",
    "-------------------------",
    "-------------------------",
    "-------------------------",
    "-------------------------",
    "-------------------------",
    "-------------------------",
    "------X----X----X---X----",
    "-------------------------",
    "-------------------------",
    "-------------------------",
    "-------------------------",
    "--XXX----XX----X----XX---",
    "-------------------------",
    "-------------------------",
    "-------------------------",
]

PR = [range(len(RowData[i])) for i in N]
PC = [range(len(ColData[i])) for i in N]

rowShifts = []
for i, row in enumerate(RowData):
    shiftLen = sum(row) + (len(row) - 1)
    rowShifts.append(len(N) - shiftLen)

colShifts = []
for i, col in enumerate(ColData):
    shiftLen = sum(col) + (len(col) - 1)
    colShifts.append(len(N) - shiftLen)

rowPatterns: List[List[Tuple]] = []
for i, row in enumerate(rowShifts):
    rowList = []
    for startingPosition in range(row + 1):
        patternList = [0 for _ in N]

        k = startingPosition

        for block in RowData[i]:
            for cell in range(block):
                patternList[k + cell] = 1
            k += block + 1
        rowList.append(tuple(patternList))
    rowPatterns.append(rowList)


colPatterns: List[List[Tuple]] = []
for i, col in enumerate(colShifts):
    colList = []
    for startingPosition in range(col + 1):
        patternList = [0 for _ in N]

        k = startingPosition

        for block in ColData[i]:
            for cell in range(block):
                patternList[k + cell] = 1
            k += block + 1
        colList.append(tuple(patternList))
    colPatterns.append(colList)

# Convert preset into binary
pre = [[0 for _ in N] for _ in N]

for i, row in enumerate(PreSet):
    for j, col in enumerate(row):
        if col == "-":
            continue
        elif col == "X":
            # Cell turned on
            pre[i][j] = 1


m = Model("Nanogram")


X = {(i, p): m.addVar(vtype=GRB.BINARY) for i in N for p in rowPatterns[i]}
Y = {(i, p): m.addVar(vtype=GRB.BINARY) for i in N for p in colPatterns[i]}


# Constraints
PreSetCells = {
    (i, j): m.addConstr(quicksum(p[j] * X[i, p] for p in rowPatterns[i]) == 1)
    for i in N
    for j in N
    if PreSet[i][j] == "X"
}

OneRow = {i: m.addConstr(quicksum(X[i, p] for p in rowPatterns[i]) == 1) for i in N}
OneCol = {j: m.addConstr(quicksum(X[j, p] for p in colPatterns[j]) == 1) for j in N}

Match = {
    (i, j): m.addConstr(
        quicksum(p[j] * X[i, p] for p in rowPatterns[i])
        == quicksum(p[i] * Y[j, p] for p in colPatterns[j])
    )
    for i in N
    for j in N
}

m.optimize()
