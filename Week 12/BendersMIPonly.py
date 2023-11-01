# -*- coding: utf-8 -*-
# %%
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
    
# The set of minutes
minutes = [-1] + list(range(deadline))

# Sets
jobs = range(num_jobs)
machines = range(num_machines)

# capacity of each machine
capacity = [10 for m in machines]

# Resource consumptions for each job (same for each machine)
consume = [np.random.randint(1, 11) for j in jobs]

# Processing time
processing_time = [[int(np.random.randint(
    m + 1, 10*(m + 1))) for j in jobs] for m in machines]

# Master problem
BMP = gp.Model()
BMP.setParam("Seed", 0)

# Variables
# X[j, m] = 1 iff job j processed by machine
X = {(j, m): BMP.addVar(vtype=gp.GRB.BINARY) for j in jobs for m in machines}

# Minimise makespan
makespan = BMP.addVar()
BMP.setObjective(makespan, gp.GRB.MINIMIZE)

# assign_to_one_machine each job to one machine
assign_to_one_machine = {j: BMP.addConstr(
    gp.quicksum(X[j, m] for m in machines) == 1) for j in jobs}

# Initial cuts
initial_cuts = {m: BMP.addConstr(makespan*capacity[m]>=gp.quicksum(
    consume[j] * processing_time[m][j] * X[j, m] for j in jobs)) for m in machines}

# Solve information
_CACHE = {}
_CACHE["FeasCuts"] = 0
_CACHE["OptCuts"] = 0
_CACHE["Time in callback"] = 0

# Callback
def Callback(model, where):
    cb_start_time = time.time()
    if where==gp.GRB.Callback.MIPSOL:

        # Retrieve incumbent solution
        XVal = model.cbGetSolution(X)
        
        # Subproblem for machine m
        for m in machines:
            
            # J = the jobs allocated to this machine
            J = [j for j in jobs if XVal[j, m] > 0.5]
            
            # Skip if no jobs
            if len(J) == 0:
                continue
            
            # Subproblem
            BSP = gp.Model()
            BSP.setParam("OutputFlag", 0)
            
            # Start time variables
            S = {(j, t): BSP.addVar(
                vtype=gp.GRB.BINARY) for j in J for t in minutes}
            
            # Constraints by job
            for j in J:
                
                # Every job must start
                BSP.addConstr(S[j, -1] == 0)
                
                # Every job must finish by the deadline
                # I.e. must start early enough to finish
                BSP.addConstr(S[j, deadline - processing_time[m][j]] == 1)
                
                # Set start times
                for t in minutes:
                    if t - 1 in minutes:
                        BSP.addConstr(S[j, t - 1] <= S[j, t])
            
            # Constraints by minute
            for t in minutes:
                
                # This expression corresponds to the total
                # resource consumption of active jobs at time t
                active_jobs = gp.quicksum(
                    consume[j] * (S[j, t] - S[j, max(t - processing_time[m][j], -1)])
                    for j in J)
                
                # capacity constraint
                BSP.addConstr(active_jobs <= capacity[m])
                
            # Makespan for this machine
            makespan_m = BSP.addVar()
            for j in J:

                # Force the makespan up
                # If job j starts at time t then it
                # finishes at time t + processing_time[m][j]
                BSP.addConstr(makespan_m >= gp.quicksum(
                    (t + processing_time[m][j]) * (S[j, t] - S[j, t - 1])
                    for t in minutes if t - 1 in minutes))
                
            # Solve the minimum makespan problem
            BSP.setObjective(makespan_m, gp.GRB.MINIMIZE)
            BSP.optimize()

            # If infeasible, can't do these jobs
            if BSP.Status == gp.GRB.INFEASIBLE:

                _CACHE["FeasCuts"] += 1
                model.cbLazy(gp.quicksum(X[j, m] for j in J) <= len(J) - 1)
            
            # If optimal, bound the makespan
            if BSP.Status == gp.GRB.OPTIMAL:

                _CACHE["OptCuts"] += 1
                model.cbLazy(makespan >= BSP.objVal - gp.quicksum(
                    processing_time[m][j]*(1 - X[j, m]) for j in J))
    
    _CACHE["Time in callback"] += time.time() - cb_start_time

   
# Solve
BMP.setParam("LazyConstraints", 1)
start_time = time.time()
BMP.optimize(Callback)
_CACHE["Runtime"] = time.time() - start_time
_CACHE["ObjVal"] = BMP.ObjVal

# %%
