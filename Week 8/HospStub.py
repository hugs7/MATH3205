from gurobipy import *

fname = "A-40-1.data"

with open(fname, "r") as f:
    nDays = int(f.readline())
    Days = range(nDays)
    Rooms = [int(f.readline()) for d in Days]
    nOps = int(f.readline())
    Ops = range(nOps)
    nSurgeons = int(f.readline())
    Surgeons = range(nSurgeons)
    nTime = int(f.readline())
    Times = range(nTime)
    SurgeonHours = []
    for d in Days:
        fields = f.readline().split()
        SurgeonHours.append([int(fields[s]) for s in Surgeons])
    fields = f.readline().split()
    Duration = [int(fields[o]) for o in Ops]
    minDuration = min(Duration)
    fields = f.readline().split()
    Surgeon = [int(fields[o])-1 for o in Ops]
    fields = f.readline().split()
    Due = [int(fields[o])-1 for o in Ops]
    fields = f.readline().split()
    Infectious = [int(fields[o])==1 for o in Ops]
        
SurgeonOps = [{o for o in Ops if Surgeon[o]==s} for s in Surgeons]

OCT=6

