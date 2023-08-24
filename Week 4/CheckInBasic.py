# Check in counters
import random
import heapq
import collections
from gurobipy import GRB, quicksum, Model

EPS = 0.0001

ServiceTime = 2 # Average passenger service time - exponentially distributed
DeskCost = 40 # Cost of opening a desk per half hour
QueueCost = 40 # Queuing cost per half hour per passenger
MaxDesks = 20 # Maximum number of desks to open

N = range(MaxDesks+1)

# Flight info
Pass = [150,210,240,180,270,150,210,300,180,270]
Start = [0,1,2,2,3,4,5,6,6,7]
Start = [2*s for s in Start]

F = range(len(Pass))

# Distribution of arrivals from start - need to all be done in final
Arrive = [5,10,20,30,20,15,0]
ArriveChoice = [i for i in range(len(Arrive)) for j in range(Arrive[i])]

# Half hour periods
T = range(max(Start)+len(Arrive)) # reduce this
L = 30

# Generate |S| scenarios
# Each entry contains arrival time, flight and service time

random.seed(25)
S = range(50)
Sim = [[] for s in S]
for s in S:
    for f in F:
        for p in range(Pass[f]):
            # Sample service time from exponential
            # Round with weight based on the fraction
            Sim[s].append(
                (L*(random.choice(ArriveChoice)+Start[f])+random.randrange(L),
                 f,random.expovariate(1/ServiceTime)))
    Sim[s].sort()
    
# Dictionaries to store starting k and desk for each sample and time period
# assuming all the time periods beforehand are at MaxDesks
K = {}
DeskStart = {}
for s in S:
    desks = [0 for i in range(MaxDesks)]
    tUpto = 0
    K[s,tUpto] = 0
    DeskStart[s,tUpto] = list(desks)
    for (i,k) in enumerate(Sim[s]):
        while tUpto < T[-1] and max(k[0],desks[0])>=(tUpto+1)*L:
            tUpto += 1
            K[s,tUpto] = i
            DeskStart[s,tUpto] = list(desks)
        agent = heapq.heappop(desks)
        heapq.heappush(desks,max(agent,k[0])+k[2])
    while tUpto < T[-1]:
        tUpto += 1
        K[s,tUpto] = i
        DeskStart[s,tUpto] = list(desks)
            
_Simulate = {}

def Simulate(s,tList):
    tTuple = tuple(tList)
    if (s,tTuple) in _Simulate:
        return _Simulate[s,tTuple]
    # tList is a list of intervals and staffing levels
    # Next available agent serves each passenger
    # Add more agents if the level goes up
    # Next available agent goes off duty if the level goes down    
    delay = {t: 0 for t in T}
    level = [MaxDesks for t in T]
    for t,l in tList:
        level[t] = l
    # Setup initial state
    tUpto = min(t for (t,_) in tList)
    tMax = max(t for (t,_) in tList)
    desks = list(DeskStart[s,tUpto])
    # Go max to the required level
    while len(desks) > level[tUpto]:
        heapq.heappop(desks)
    # Stop when we are done
    for k in Sim[s][K[s,tUpto]:]:
        if k[0]//L > tMax:
            break
        OverFlow = False
        # Have we crossed a time period boundary
        while len(desks)==0 or max(k[0],desks[0])>=(tUpto+1)*L:                
            if tUpto>=T[-1]:
                OverFlow = True
                break
                #print("********* Fell off the end", k, desks)
            # Open and shut desks
            if level[tUpto+1]>level[tUpto]:
                # Add agents
                for i in range(level[tUpto+1]-level[tUpto]):
                    heapq.heappush(desks,L*(tUpto+1))
            elif level[tUpto+1]<level[tUpto]:
                # Remove agents
                for i in range(level[tUpto]-level[tUpto+1]):
                    heapq.heappop(desks)
            tUpto+=1
        # Serve each passenger in the simulation
        if OverFlow:
            delay[k[0]//L] += len(T)*L
        else:
            agent = heapq.heappop(desks)
            delay[k[0]//L] += max(0,agent-k[0])
            heapq.heappush(desks,max(agent,k[0])+k[2])
    
    _Simulate[s,tTuple] = delay
    return delay
    
m = Model()
Y = {t: m.addVar(vtype=GRB.INTEGER, ub=MaxDesks) for t in T}
Z = {(n,t): m.addVar(vtype=GRB.BINARY) for n in N for t in T}
Theta = {(s,t): m.addVar() for s in S for t in T}

m.setObjective((quicksum(DeskCost*Y[t] for t in T) + 
               QueueCost * quicksum(Theta[s,t] for s in S for t in T) / len(S)*L))

ClearFutureWork = {t:
    m.addConstr(L*quicksum(Y[tt] for tt in T[t:])>=
        max(sum(k[2] for k in Sim[s] if k[0]>=t*L) for s in S))
    for t in T}
    
ClearEachFlight = {t:
    m.addConstr(L*quicksum(Y[tt] for tt in T[:t+1])>=
        max(sum(k[2] for k in Sim[s] if Start[k[1]]+len(Arrive)<=t) for s in S))
    for t in T}
    


m.optimize()

Level = [(t,int(Y[t].x)) for t in T]
TotalDelay = sum(sum(Simulate(s,Level).values()) for s in S)
print('Agent Cost =', m.objVal)
print('Delay cost=', QueueCost*TotalDelay/len(S)/L)


