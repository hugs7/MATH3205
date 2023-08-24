from gurobipy import *
import random

# Size of board
nMax = 10
N = range(nMax)
# Max time
T = range(8)
# Number of vehicles
V = range(2)

def Neighbours(i,j):
    tList = []
    if i > 0:
        tList.append((i-1,j))
    if i < nMax - 1:
        tList.append((i+1, j))
    if j > 0:
        tList.append((i,j-1))
    if j < nMax - 1:
        tList.append((i, j+1))
    return tList

random.seed(5)
C = [[random.randint(0,4) for j in N] for i in N]

for c in C:
    print (c)
