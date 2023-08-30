import math
import random
from gurobipy import *
import pylab

def Distance(p1, p2):
  return int(math.hypot(p1[0] - p2[0], p1[1] - p2[1]) + 0.5)

nTrips = 800
nLocs = 100
nDepots = 5
Trips = range(nTrips)
Locs = range(nLocs)
Depots = range(nDepots)

# The points are chosen in a region of size Square*Square
# The travel time/cost trades off against the BusCost
Square = 240
BusCost = 100
random.seed(3)

# Set up random locations but set some of the positions to be corners
# of the grid.  The depots are the first nDepots positions
Pos = [(random.randint(0,Square), random.randint(0,Square)) for i in Locs]
Pos[0] = (0,0)
Pos[1] = (Square,Square)
Pos[2] = (0, Square)
Pos[3] = (Square, 0)
Pos[4] = (Square/2, Square/2)
D = [[Distance(Pos[i], Pos[j]) for j in Locs] for i in Locs]

# Set up some timetabled bus trips.  Each trip t has:
#	Start Location/End Location 	TripLoc[t][0/1]
#	Start Time/End Time		TripTime[t][0/1]
#	Allowable depots		TripDep[t][d]==1 if allowable

# Start and end location of each trip
TripLoc = [(random.choice(Locs), random.choice(Locs)) for i in Trips]

def GenerateTimes(i):
  # Generate a start and end time for a trip
  start = random.randint(240,1440 - D[TripLoc[i][0]][TripLoc[i][1]] - 60)
  end = start + D[TripLoc[i][0]][TripLoc[i][1]] + random.randint(30,60)
  return (start, end)

def GenerateDepots():
  # Generate a list of 0's and 1's corresponding to
  # whether the trip can use the depot
  alist = [0 for i in Depots]
  for i in Depots:
    if random.random() <= 0.5:
      alist[i] = 1
  if sum(alist) == 0:
    alist[random.choice(Depots)] = 1
  return list(alist)

TripTime = [GenerateTimes(i) for i in Trips]
TripDep = [GenerateDepots() for i in Trips]

# Succ and Pred contain the trips that can come after/before a trip
# with a bus from the specified depot

Succ = {(t,d): set() for t in Trips for d in Depots if TripDep[t][d]}
Pred = {(t,d): set() for (t,d) in Succ}

for (t1,d) in Succ:
    for t2 in Trips:
        if TripDep[t2][d] and \
            TripTime[t2][0]>=TripTime[t1][1]+D[TripLoc[t1][1]][TripLoc[t2][0]]:
            Succ[t1,d].add(t2)
            Pred[t2,d].add(t1)

# Trip to trip travel times - only required values
TravTT = {(t1,t2): D[TripLoc[t1][1]][TripLoc[t2][0]] 
          for t1 in Trips 
          for t2 in set.union(*(Succ[t1,d] for d in Depots if (t1,d) in Succ))}
# Trip to depot and depot to trip travel times
TravTD = {(t,d): D[TripLoc[t][1]][d] for (t,d) in Succ}
TravDT = {(d,t): D[d][TripLoc[t][0]] for (t,d) in Succ}

# We want to create schedules for buses
# Start at the depot and make a chain of trips.
# Minimise the fixed cost of buses plus the total distance travelled 
# to connect trips.