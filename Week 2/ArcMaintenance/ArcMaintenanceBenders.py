from gurobipy import GRB, quicksum, Model

EPS = 1e-6
# Initialise empty data
Nodes = []
Arcs = []
BackArc = None
FromNode = -1

# Read in the data
with open('Outmax_flow2.dat') as f:
    while True:
        l = f.readline().strip()
        if l[0]=='n':
            FromNode = len(Nodes)
            Nodes.append(l)
        elif l[0]=='a':
            t = l.split(' ')
            flow = int(t[4])
            ToNode = int(t[3])
            if flow==10000:
                BackArc = len(Arcs)
            Arcs.append((FromNode,ToNode,flow))
        else:
            break
N = range(len(Nodes))
A = range(len(Arcs))

print('Nodes and Arcs', len(Nodes), len(Arcs))

# Empty array of jobs
Jobs = []
with open('max_flow2.dat_Job0') as f:
    while True:
        l = f.readline().strip()
        if len(l) <= 1:
            break
        nArc = int(l.split(' ')[1])
        t = f.readline().strip().split(' ')
        Jobs.append((nArc,int(t[1])-1,int(t[2])-1,int(t[3])))
        
T = range(1000)
J = range(len(Jobs))
# The jobs for an arc
JobsA = [[j for j in J if Jobs[j][0]==a] for a in A]
# The starting time periods for job A
JP = [range(Jobs[j][1], Jobs[j][2]) for j in J]

print('Jobs', len(Jobs))
# The jobs and their indices that impact on arc a in time t
JobsTA = [[[(j,p) for j in JobsA[a] for p in JP[j] if p<=t and p+Jobs[j][3]>t]
           for a in A] for t in T]
print('Calculated JobsTA')

BSP = Model()
BSP.setParam('OutputFlag',0)
X = {a: BSP.addVar() for a in A}

BSP.setObjective(X[BackArc], GRB.MAXIMIZE)

FlowConservation = {n:
    BSP.addConstr(quicksum(X[a] for a in A if Arcs[a][0]==n)==
                quicksum(X[a] for a in A if Arcs[a][1]==n))
    for n in N}

UpperBound = {a:
    BSP.addConstr(X[a]<=Arcs[a][2])
    for a in X}

BSP.optimize()

    
BMP = Model()
BMP.setParam('OutputFlag',0)

Y = {(j,t): BMP.addVar(vtype=GRB.BINARY) for j in J for t in JP[j]}
Theta = {t: BMP.addVar(ub=BSP.objVal) for t in T}

BMP.setObjective(quicksum(Theta[t] for t in T), GRB.MAXIMIZE)

EachJobOnce = {j:
    BMP.addConstr(quicksum(Y[j,t] for t in JP[j])==1)
    for j in J}
    
for k in Y:
    Y[k].vtype = GRB.CONTINUOUS
while True:    
    BMP.optimize()
    CalcObj = 0
    CutsAdded = 0
    for t in T:
        for a in A:
            UpperBound[a].RHS = Arcs[a][2]* \
            (1-sum(Y[j,td].x for (j,td) in JobsTA[t][a]))
        BSP.optimize()
        CalcObj += BSP.objVal
        if BSP.objVal < Theta[t].x-EPS:
            # Time to add a cut
            CutsAdded += 1
            BMP.addConstr(Theta[t]<=quicksum(
                UpperBound[a].pi*(Arcs[a][2]* 
                (1-quicksum(Y[j,td] for (j,td) in JobsTA[t][a]))) 
                for a in A))
    print(CutsAdded, BMP.objVal, CalcObj)
    if CutsAdded==0:
        break

for k in Y:
    Y[k].vtype = GRB.BINARY
while True:    
    BMP.optimize()
    CalcObj = 0
    CutsAdded = 0
    for t in T:
        for a in A:
            UpperBound[a].RHS = Arcs[a][2]* \
            (1-sum(Y[j,td].x for (j,td) in JobsTA[t][a]))
        BSP.optimize()
        CalcObj += BSP.objVal
        if BSP.objVal < Theta[t].x-EPS:
            # Time to add a cut
            CutsAdded += 1
            BMP.addConstr(Theta[t]<=quicksum(
                UpperBound[a].pi*(Arcs[a][2]* 
                (1-quicksum(Y[j,td] for (j,td) in JobsTA[t][a]))) 
                for a in A))
    print(CutsAdded, BMP.objVal, CalcObj)
    if CutsAdded==0:
        break
                