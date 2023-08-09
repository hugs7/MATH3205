from gurobipy import GRB, quicksum, Model

# Initialise empty data
Nodes = []
Arcs = []
Omega = None
FromNode = -1
EPS= 0.00001
FlowINF = 10000

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
            if flow==FlowINF:
                Omega = len(Arcs)
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
JobsTA = [[{(j,p) for j in JobsA[a] for p in JP[j] if p<=t and p+Jobs[j][3]>t}
           for a in A] for t in T]
print('Calculated JobsTA')

# Set up the sub-problem
BSP = Model()
BSP.setParam('OutputFlag',0)
X = {a: BSP.addVar() for a in A}

BSP.setObjective(X[Omega],GRB.MAXIMIZE)

FlowConservation = {n:
    BSP.addConstr(quicksum(X[a] for a in A if Arcs[a][0]==n)==
                quicksum(X[a] for a in A if Arcs[a][1]==n))
    for n in N}

UpperBound = {a:
    BSP.addConstr(X[a]<=Arcs[a][2])
    for a in A}
# Solve unrestricted sub-problem to calculate MaxFlow
BSP.optimize()
MaxFlow = BSP.objVal
print('Maximum flow', MaxFlow)

# Set up master problem
BMP = Model()
Y = {(j,t): BMP.addVar(vtype=GRB.BINARY) for j in J for t in JP[j]}
Theta = {t: BMP.addVar(ub=MaxFlow) for t in T }

BMP.setObjective(quicksum(Theta[t] for t in T), GRB.MAXIMIZE)

EachJobScheduled = {j:
    BMP.addConstr(quicksum(Y[j,t] for t in JP[j])==1)
    for j in J}  
    
_SolveBSP = {}
SolvesCalled = 0

def SolveBSP(AZero):
    global SolvesCalled
    SolvesCalled += 1
    if AZero not in _SolveBSP:
        for a in A:
            if a in AZero:
                UpperBound[a].RHS = 0
            else:
                UpperBound[a].RHS = Arcs[a][2]
        BSP.optimize()
        _SolveBSP[AZero] = (BSP.objVal, {a: UpperBound[a].pi for a in A})
    return _SolveBSP[AZero]

BMP._Best = 0
            
def Callback(model,where):
    if where==GRB.Callback.MIPSOL:
        YV = model.cbGetSolution(Y)
        YSet = {k for k in YV if YV[k]>0.9}
        ThetaV = model.cbGetSolution(Theta)
        
        TotalObj = 0
        CutsAdded = 0
        for t in T:
            AZero = frozenset(a for a in A if JobsTA[t][a] & YSet)
            Obj, Pi = SolveBSP(AZero)
            TotalObj += Obj
            if Obj < ThetaV[t] - EPS:
                model.cbLazy(Theta[t]<=quicksum(
                        Pi[a]*Arcs[a][2]*
                        (1-quicksum(Y[j,tt] for (j,tt) in JobsTA[t][a])) 
                        for a in A))
                CutsAdded += 1
            ThetaV[t] = Obj
        # Test if TotalObj is better than the incumbent
        if CutsAdded > 0 and TotalObj > model._Best+EPS:
            # Save the solution away
            print('#### Saving', TotalObj)
            model._Best = TotalObj
            model._Y = [YV[k] for k in Y]
            model._Theta = [ThetaV[k] for k in Theta]
        elif TotalObj > model._Best:
            model._Best = TotalObj
            
            
    if where==GRB.Callback.MIPNODE and model.cbGet(GRB.Callback.MIPNODE_STATUS)==GRB.OPTIMAL:
        # Do we have a saved solution that is better than the incumbent?
        if model._Best > model.cbGet(GRB.Callback.MIPNODE_OBJBST)+EPS:
            # If so, suggest it to Gurobi
            model.cbSetSolution(list(Y.values()),model._Y)
            model.cbSetSolution(list(Theta.values()),model._Theta)
                
# Warm start!
# Count = 1
# while True:
#     BSP.optimize()
#     if BSP.objVal>=2*MaxFlow:
#         break
#     print(Count, BSP.objVal)
#     Count+=1
#     for t in T:
#         BMP.addConstr(Theta[t]<=quicksum(
#                 UpperBound[a].pi*Arcs[a][2]*
#                 (1-quicksum(Y[j,tt] for (j,tt) in JobsTA[t][a])) 
#                     for a in A))
#     for a in A:
#         if UpperBound[a].pi > EPS:
#             UpperBound[a].RHS += FlowINF

# Relax the problem
for k in Y:
    Y[k].vType = GRB.CONTINUOUS

# Add Benders cuts in a loop
BMP.setParam('OutputFlag',0)
while True:
    BMP.optimize()
    CutsAdded = 0
    for t in T:
        for a in A:
            UpperBound[a].RHS = Arcs[a][2]*(1-sum(Y[j,tt].x for (j,tt) in JobsTA[t][a]))
        BSP.optimize()
        if BSP.objVal < Theta[t].x - EPS:
            CutsAdded += 1
            BMP.addConstr(Theta[t]<=quicksum(
                    UpperBound[a].pi*Arcs[a][2]*
                    (1-quicksum(Y[j,tt] for (j,tt) in JobsTA[t][a])) 
                        for a in A))
    
    if CutsAdded==0:
        break
    print('Added', CutsAdded, BMP.objVal)
    
BMP.setParam('OutputFlag',1)
# Make the problem integer again
for k in Y:
    Y[k].vType = GRB.BINARY

                
    
BMP.setParam('MIPGap',0)
BMP.setParam('LazyConstraints',1)
# BMP.setParam('BranchDir',1)
BMP.optimize(Callback)