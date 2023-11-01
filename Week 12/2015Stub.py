# Stub for MATH4202 2015 Prac exam

from gurobipy import *

# The data for the squares
Data1 = [
[0,0,0,0,0,0],
[3,2,3,2,2,2],
[0,0,2,3,2,2],
[2,0,2,2,0,0],
[0,2,3,0,2,2],
[2,3,0,2,0,4]
]

Data2 = [
[3,2,2,3,2,1,3,2,2,0,2,0],
[2,3,2,3,2,0,2,3,2,3,2,3],
[0,1,3,1,2,2,0,1,3,1,2,2],
[1,1,0,1,3,1,1,1,0,3,0,1],
[2,2,1,3,3,1,2,2,1,3,3,1],
[3,2,1,1,2,2,3,2,1,1,2,2],
[3,2,2,1,2,0,3,2,2,0,2,0],
[2,3,2,3,2,2,2,3,2,3,2,0],
[0,1,3,1,2,2,0,1,3,1,2,2],
[1,1,0,0,2,1,1,1,1,0,2,1],
[2,2,1,3,3,1,2,2,1,3,3,1],
[3,2,1,1,2,2,3,2,1,1,2,2]
]

# Change this next line to test with Data1 or Data2
Data = Data1

# The size of the square
N = range(len(Data))

SOut = {(i,j) for i in N for j in N if Data[i][j]>0}
SIn = {(i,j) for i in N for j in N}

T = range(len(SOut))
maxT = T[-1]+1

def MoveTo(s):
    # Return the squares we can move to from square s
    retList = set()
    i,j = s
    d = Data[i][j]
    for di in [-d,0,d]:
        for dj in [-d,0,d]:
            if (di!=0 or dj!=0) and (i+di,j+dj) in SIn:
                retList.add((i+di,j+dj))
    return retList

# Set this to True to test the PartB code, or false for the PartD code
PartB = True

if PartB:
    # Put the Part B code here.
    pass
else:
    # Put the Part D code here
    pass