import math
import gurobipy as gp
import sys
fName = "PH1_S2_C150_1.txt"
if len(sys.argv) > 1:
    fName = sys.argv[1]


# Supplier co-ordinate
Supp = []
# Customer
COORD = 0
READY = 1
DUE = 2
SERVICE = 3
WEIGHT = 4
SUPP = 5
Cust = []

with open(fName) as f:
    f.readline()
    l = [i for i in f.readline().split(" ") if len(i) > 0]
    nS = int(l[0])
    nC = int(l[1])
    S = range(nS)
    C = range(nC)
    for i in range(3):
        f.readline()
    for s in S:
        l = [i for i in f.readline().split(" ") if len(i) > 0]
        Supp.append((int(l[1]),int(l[2])))
    for c in C:
        l = [i for i in f.readline().split(" ") if len(i) > 0]
        Cust.append(((int(l[1]),int(l[2])),int(l[3]),int(l[4]),int(l[5]),round(100*float(l[6])),int(l[7])-1))

def Time(c1,c2):
    # return int(math.hypot(c1[0],c1[1])/10)
    return math.ceil(math.hypot(c1[0]-c2[0],c1[1]-c2[1])/3)

T = {(i,s): Time(Cust[i][COORD],Supp[s]) for i in C for s in S}
