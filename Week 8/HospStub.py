from gurobipy import GRB, quicksum, Model
import os

fname = os.path.join("Week 8", "C-80-2.data")

with open(fname, "r") as f:
    # Number of days
    nDays = int(f.readline())

    # Days as a set
    Days = range(nDays)

    # Set of operating rooms
    Rooms = [int(f.readline()) for d in Days]

    # Number of operations
    nOps = int(f.readline())

    # Operations sets
    Ops = range(nOps)

    # Number of surgeons
    nSurgeons = int(f.readline())

    # Surgeon set
    Surgeons = range(nSurgeons)

    # Number of timeslots
    nTime = int(f.readline())

    # Timeslots set
    Times = range(nTime)

    # Calculate number of hours each surgeon is available each day
    SurgeonHours = []
    for d in Days:
        fields = f.readline().split()
        SurgeonHours.append([int(fields[s]) for s in Surgeons])

    # Duration of each operation
    fields = f.readline().split()
    Duration = [int(fields[o]) for o in Ops]

    # Minimum duration of any operation
    minDuration = min(Duration)
    fields = f.readline().split()

    # Surgeon Assigned to each Operation
    Surgeon = [int(fields[o]) - 1 for o in Ops]
    fields = f.readline().split()

    # Due date for each operation
    Due = [int(fields[o]) - 1 for o in Ops]

    # Binary value if operation is infectious or not
    fields = f.readline().split()
    Infectious = [int(fields[o]) for o in Ops]

# Which operation each surgon is assigned to.
SurgeonOps = [{o for o in Ops if Surgeon[o] == s} for s in Surgeons]
OCT = 6

# Nodes
Nodes = set()
for d in Days:
    # Starting time
    Nodes.add((d, 0, 0))
    # Ending times
    Nodes.add((d, nTime, 0))
    Nodes.add((d, nTime, 1))
    # Intermediary nodes
    for t in Times[minDuration : nTime - minDuration + 1]:
        Nodes.add((d, t, 0))
        Nodes.add((d, t, 1))

# Make arcs
Arcs = set()

for d in Days:
    # waiting arcs
    for t in Times[minDuration : nTime - minDuration]:
        Arcs.add(((d, t, 0), (d, t + 1, 0), -1))
        Arcs.add(((d, t, 1), (d, t + 1, 1), -1))

    # Cleaning arcs
    for t in Times[minDuration : nTime - minDuration - OCT + 1]:
        Arcs.add(((d, t, 1), (d, t + OCT, 0), -1))

    # Operating / servicing arcs
    for i in Ops:
        if Due[i] >= d and SurgeonHours[d][Surgeon[i]] >= Duration[i]:
            Arcs.add(((d, 0, 0), (d, Duration[i], Infectious[i]), i))
            for t in Times[minDuration:]:
                if (d, t + Duration[i], 0) in Nodes:
                    Arcs.add(((d, t, 0), (d, t + Duration[i], Infectious[i]), i))
                    if Infectious[i]:
                        Arcs.add(((d, t, 1), (d, t + Duration[i], Infectious[i]), i))

for a in Arcs:
    if a[0] not in Nodes or a[1] not in Nodes:
        print("Node missing")

# Define Model
m = Model("Operating Theatre")

# Variables
X = {a: m.addVar(vtype=GRB.INTEGER) for a in Arcs}

# Objective
m.setObjective(quicksum(Duration[a[2]] * X[a] for a in Arcs if a[2] >= 0), GRB.MAXIMIZE)


# Constriants
# One operation per timeslot per surgeon

for s in Surgeons:
    for d in Days:
        if SurgeonHours[d][s] > 0:
            for t in Times[minDuration - 1 : nTime - minDuration + 1]:
                m.addConstr(
                    quicksum(
                        X[a]
                        for a in Arcs
                        if a[0][0] == d
                        and a[2] >= 0
                        and Surgeon[a[2]] == s
                        and a[0][1] <= t
                        and a[1][1] > t
                    )
                    <= 1
                )


# Surgon Hours Limit
SurgeonHoursLimit = {
    (s, d): m.addConstr(
        quicksum(
            Duration[a[2]] * X[a]
            for a in Arcs
            if a[0][0] == d and a[2] >= 0 and Surgeon[a[2]] == s
        )
        <= SurgeonHours[d][s]
    )
    for s in Surgeons
    for d in Days
    if SurgeonHours[d][s] > 0
}

# Do mandatory operations
Mandatory = {
    i: m.addConstr(quicksum(X[a] for a in Arcs if a[2] == i) == 1)
    for i in Ops
    if Due[i] <= Days[-1]
}

# Optional operations at most once

Optional = {
    i: m.addConstr(quicksum(X[a] for a in Arcs if a[2] == i) <= 1)
    for i in Ops
    if Due[i] > Days[-1]
}

# Limit operating theatres
TheatresPerDay = {
    d: m.addConstr(quicksum(X[a] for a in Arcs if a[0] == (d, 0, 0)) <= Rooms[d])
    for d in Days
}

# Converse Flow
Conserve = {
    n: m.addConstr(
        quicksum(X[a] for a in Arcs if a[1] == n)
        == quicksum(X[a] for a in Arcs if a[0] == n)
    )
    for n in Nodes
    if n[1] >= minDuration and n[1] <= nTime - minDuration
}

breakpoint()
m.optimize()

print(m.objVal)

for d in Days:
    DayOps = []
    for a in Arcs:
        if a[0][0] == d and a[2] >= 0 and X[a].x > 0.9:
            DayOps.append(a)

    DayOps.sort()
    print(d, ":", DayOps)

    print("---")
