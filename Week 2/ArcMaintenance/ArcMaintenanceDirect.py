from gurobipy import Model, quicksum, GRB

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

m = Model()

Y = {(j,t): m.addVar(vtype=GRB.BINARY) for j in J for t in JP[j]}
X = {(a,t): m.addVar() for a in A for t in T}

m.setObjective(quicksum(X[BackArc,t] for t in T), GRB.MAXIMIZE)

EachJobOnce = {j:
    m.addConstr(quicksum(Y[j,t] for t in JP[j])==1)
    for j in J}
    
FlowConservation = {(n,t):
    m.addConstr(quicksum(X[a,t] for a in A if Arcs[a][0]==n)==
                quicksum(X[a,t] for a in A if Arcs[a][1]==n))
    for n in N for t in T}

UpperBound = {(a,t):
    m.addConstr(X[a,t]<=Arcs[a][2]*
                (1-quicksum(Y[j,tt] for (j,tt) in JobsTA[t][a])))
    for (a,t) in X}

m.optimize()
