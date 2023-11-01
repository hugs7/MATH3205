# %%

import gurobipy as gp
import numpy as np
import time

np.random.seed(seed=0)

# Instance generation
NumJobs = 15
NumMachines = 2

# Time horizon
alpha = 1 / 3
Deadline = round(alpha * (5 * NumJobs)*(NumMachines + 1)/NumMachines)

# Sets
Jobs = range(NumJobs)
Machines = range(NumMachines)

# Capacity of each machine
Capacity = [10 for m in Machines]

# Resource consumptions same for each facility
Consume = [np.random.randint(1, 11) for j in Jobs]

# Processing time
ProcessingTime = [
    [int(np.random.randint(m + 1, 10*(m + 1))) for j in Jobs]
    for m in Machines]
