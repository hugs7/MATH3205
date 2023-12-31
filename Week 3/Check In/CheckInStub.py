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
    
# Discrete event simulation
def Simulate(s,level):
    # Next available agent serves each passenger
    # Add more agents as if the level goes up
    # Next available agent goes off duty if the level goes down
    
    TotDelay = 0
    # Setup initial state
    desks = []
    for i in range(level[0]):
        heapq.heappush(desks,0)
    tUpto = 0       # Time up to
    for k in Sim[s]:     # For each people in this scenario/simulation
        # Have we crossed a time period boundary
        while tUpto < T[-1] and (len(desks)==0 or max(k[0],desks[0])>=(tUpto+1)*L):                
            if tUpto>=T[-1]:
                print("********* Fell off the end", k, desks)
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
        agent = heapq.heappop(desks)
        TotDelay += max(0,agent-k[0])
        heapq.heappush(desks,max(agent,k[0])+k[2])
    
    return TotDelay
    


m = Model()

# Variables
Y = {t: m.addVar(vtype=GRB.INTEGER, ub=MaxDesks) for t in T}


# Data is above

# Objective

m.setObjective(quicksum(DeskCost*Y[t] for t in T))

ClearFutureWork = {t: m.addConstr(L*quicksum(Y[t_prime] for t_prime in T[t:])>=
                                  max(sum(k[2] for k in Sim[s] if k[0] >= t*L) for s in S)) for t in T}

ClearEachFlight = {t: m.addConstr(L*quicksum(Y[t_prime] for t_prime in T[:t+1]) >=
                                  max(sum(k[2] for k in Sim[s] if Start[k[1]]+len(Arrive) <= t) for s in S)) for t in T}

m.optimize()

Level = [int(Y[t].x) for t in T]
print("Level:", Level)
TotalDelay = sum(Simulate(s,Level) for s in S)
print("Agent Cost = ", m.objVal)
print("Delay Cost = ", QueueCost*TotalDelay / len(S) / L)

print(m.objVal)