# %%
from ortools.sat.python import cp_model
import gurobipy as gp
import numpy as np
import time

np.random.seed(seed=0)

# Instance generation
num_jobs = 30
num_machines = 4

# Time horizon
alpha = 1 / 3
deadline = round(alpha * (5 * num_jobs)*(num_machines + 1)/num_machines)

# Sets
jobs = range(num_jobs)
machines = range(num_machines)

# Capacity of each machine
capacity = [10 for m in machines]

# Resource consumptions same for each facility
consume = [np.random.randint(1, 11) for j in jobs]

# Processing time
processing_time = [
    [int(np.random.randint(m + 1, 10*(m + 1))) for j in jobs]
    for m in machines]

# Create model
CP = cp_model.CpModel()

# Makespan variable
MSpan = CP.NewIntVar(0, deadline, "MSpan")

# Allocation variables
X = {(j, m): CP.NewBoolVar("X({j}, {m})") for j in jobs for m in machines}

S = {}  # Start times
E = {}  # End times
L = {}  # Lengths
I = {}  # Intervals
for j in jobs:
    for m in machines:

        # Start and end time boundaries
        EEarliest = min(processing_time[m][j] for m in machines)
        SLatest = deadline - EEarliest
        
        # Start and end times and lengths
        S[j, m] = CP.NewIntVar(0, deadline - processing_time[m][j], f"S({j})")
        E[j, m] = CP.NewIntVar(0, deadline, f"E({j})")
        
        # Interval variable
        I[j, m] = CP.NewOptionalIntervalVar(S[j, m], processing_time[m][j], E[j, m], X[j, m], f"Int({j})")

    # Assign to one machine
    CP.AddExactlyOne(X[j, m] for m in machines)

for m in machines:
    # Resource usage
    CP.AddCumulative([I[j, m] for j in jobs], [consume[j] for j in jobs], capacity[m])

# Minimize makespan
CP.AddMaxEquality(MSpan, [E[j, m] for j in jobs for m in machines])
CP.Minimize(MSpan)

# Solve CP problem
start_time = time.time()
solver = cp_model.CpSolver()
status = solver.Solve(CP)
total_time = time.time() - start_time
            
# If the problem is infeasible
if status == cp_model.INFEASIBLE:
    print("INFEASIBLE")

if status == cp_model.OPTIMAL:
    print(solver.Value(MSpan))
    print("Time:", total_time)

   

# %%
