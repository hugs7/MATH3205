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

# Calculate the earliest and latest time at each location
Early = [min(c[READY] for c in Cust if c[SUPP]==s) for s in S]
Late = [max(c[DUE]-c[SERVICE] for c in Cust if c[SUPP]==s) for s in S]

Nodes = {(s,t) for s in S for t in range(Early[s],Late[s]+1)}
Depot = (-1,-1)
# Nodes.add(Depot)

# Arc data
FROM = 0
TO = 1
COST = 2
COVER = 3

VehCost = 0

Arcs = set()
# Starting arcs
for s in S:
    Arcs.add((Depot,(s,Early[s]),VehCost,-1))
# Waiting arcs
for s in S:
    for t in range(Early[s],Late[s]+1):
        Arcs.add(((s,t),(s,t+1),0,-1))
# Service arcs
for i,c in enumerate(Cust):
    for t in range(c[READY],c[DUE]-c[SERVICE]+1):
        for s in S:
            Arcs.add((
                (c[SUPP],t),
                (s,t+c[SERVICE]+T[i,s]),
                (t-c[READY])*c[WEIGHT],
                i))
        
m = gp.Model()

X = {a: m.addVar(vtype=gp.GRB.INTEGER) for a in Arcs}

Coverage = {i:
    m.addConstr(gp.quicksum(X[a] for a in Arcs if a[COVER]==i)==1)
    for i in C}
    
ConserveFlow = {n:
    m.addConstr(gp.quicksum(X[a] for a in Arcs if a[FROM]==n)==
                gp.quicksum(X[a] for a in Arcs if a[TO]==n))
    for n in Nodes}

m.setParam('MIPGap',0)
m.setObjective(gp.quicksum(X[a] for a in Arcs if a[FROM]==Depot))
m.optimize()

print('Fixing vehicles to', round(m.objVal))
m.addConstr(gp.quicksum(X[a] for a in Arcs if a[FROM]==Depot)==round(m.objVal))

m.setObjective(gp.quicksum(a[COST]*X[a] for a in Arcs))

m.optimize()