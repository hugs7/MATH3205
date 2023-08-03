from gurobipy import Model, quicksum, GRB

EPS = 0.0001

Resources = ["Lumber", "Finishing", "Carpentry"]
Products = ["Desk", "Table", "Chair"]

R = range(len(Resources))
P = range(len(Products))

Cost = [2,4,5.2]
Input = [
        [8,6,1],
        [4,2,1.5],
        [2,1.5,0.5]]

Prob = [0.3,0.4,0.3]
S = range(len(Prob))

Demand = [
    [50,150,250],
    [20,110,250],
    [200,225,500]]

Sell = [60,40,10]

# --- Define master problem first as BMP ---
BMP = Model("Dakota Master Problem")

# --- Variables in master problem ---

# Y defines the unit qty of resources purchased in the primal (Master) 
# problem for each resource r in R
Y = {r: BMP.addVar() for r in R}

# Define theta_s which is the contribution from each subproblem
# Ensure to set the lower bound for Theta as Gurobi will set this to 0 by default
# However, in this model, Theta will always be negative.
# Lower bound will be at least the negative of the product of demand in that scenario 
# multiplied by the selling price summed over the three products p in P.
Theta = {s: BMP.addVar(lb=-sum(Demand[p][s] * Sell[p] for p in P)) for s in S}

# Set Master problem's objective
BMP.setObjective(quicksum(Cost[r] * Y[r] for r in R) + quicksum(Theta[s] * Prob[s] for s in S), GRB.MINIMIZE)

# Not required but set non-negativity on Y
# {r: BMP.addConstr(Y[r] >= 0) for r in R}

reachedOptimal = False
iter = 0

while not reachedOptimal:
    # This loop defines the iteration for cuts made.
    # We begin by optimising the master problem (at the beginning of each iteration)
    # This is because we've added an optimality constraint (cut) to the master problem 
    # at the end of the last iteration (or we're at the first iteration and need to get 
    # a starting objective value).
    BMP.optimize()

    # Disable the output flag for the master problem. Again, we don't need to see the 
    # details for each loop. We are only interested in the value of the final solution
    BMP.setParam("OutputFlag", 0)
    print("Iteration " + str(iter) + ": Master Problem Objective: " + str(BMP.objVal))

    # Initialise a counter for the number of cuts added in __this__ iteration of the problem
    numCuts = 0

    for s in S:
        # Observe this loop is within the k loop becauase we need to 
        # Optimise the sub-problem for the given Y[r]^* value that 
        # Gurobi found in the objective to the BMP just above.

        # Define the subproblem s (in this problem, scenario) as BSP
        BSP = Model("Dakota Sub-problem for scenario " + str(s))

        # Disable output for the subproblem as the details aren't required here.
        BSP.setParam("OutputFlag", 0)
        
        # --- Variables in subproblem ---

        # X is the unit qty of products p in P sold in scenario s.
        # Observe here we do not define an s index because each subproblem
        # is independent of what actual scenario we're in. We just need a variable
        # for each product and NOT for each scenario as well
        X = {p: BSP.addVar() for p in P}
        # NOT X = {(p,s): BSP.addVar() for p in P for s in S}

        # --- Sub-problem Objective ---

        # In this subproblem, we are minimising the negative of the revenue
        # That's equivalent to maximising the revenue = selling price of product
        # p multiplied by unit qty sold, X[p] summed over all products, P.
        BSP.setObjective(- quicksum(X[p] * Sell[p] for p in P), GRB.MINIMIZE)

        # --- Constraints ---

        # Resource Limit
        # Limits the usage of resources (resources required * unit qty used) 
        # to at most the availble resource Y[r] for each resource r in R
        ResourceLimit = {r: BSP.addConstr(quicksum(Input[r][p] * X[p] for p in P) <= Y[r].x) for r in R}
        # Note I've accessed Y[r] by using .x because Y isn't part of the sub-problem -
        # it is part of the master problem!

        # Demand Limit
        # Limits unit qty sold to the demand for product p (given that we are 
        # already in scenario s (in S))
        DemandLimit = {p: BSP.addConstr(X[p] <= Demand[p][s]) for p in P}

        # Not required but I'll add the non-negativity constraint for X anyway
        # NonNegativity = {p: BSP.addConstr(X[p] >= 0) for p in P}

        # Optimise the sub-problem given the constraints defined above.
        # After optimizing, we want to make a cut (see below)
        BSP.optimize()


        # --- Optimality Cut ---

        # We only need to add a cut if it's actually going to benefit us. We can do this by checking to 
        # see if the objective value of the sub-problem is greater than the existing Theta value (corresponding)
        # to this scenario s in S.
        # Observe we define an Epsilon close to 0^+ as a buffer
        if BSP.objVal > Theta[s].x + EPS:                
            # Given these constraints we've just added to the subproblem, add the corresponding
            # Duality constriant to the master. This works because if the sub-problem's 
            # constraint is binding (e.g. all the Lumber is used up), this means the 
            # corresponding dual variable's value (ResourceLimit[(index for Lumber)].pi) is
            # non-zero. Therefore, meaning that the lower bound has just increased
            # A tigher lower bound on the master problem pulls us closer to the optimal objective value
            BMP.addConstr(Theta[s] >=   quicksum(ResourceLimit[r].pi * Y[r] for r in R) +
                                        quicksum(DemandLimit[p].pi * Demand[p][s] for p in P))
            # Observe the way I've accessed these dual variables. Above I've set the constraints
            # for the sub-problem to a dictionary and then I'm indexing into that dictionary and 
            # accessing the property pi (which in Gurobi is the dual variable value of a constraint)
            # Also observe, I'm accessing Theta and Y as variables because they are part of the Master
            # problem and I am adding them to the master problem. So don't use .x here

            # Increment the cut counter
            numCuts += 1
        
        # In the second case, if the objective value is less than the current epsilon, we know something
        # has likely gone wrong. This should never happen as we are always increasing (making less negative) 
        # the objective value of the sub-problem. As a refresher, recall the sub-problem's objective is to 
        # minimize the negative of the revenue. However, as we add more and more cuts, we'll be only able to 
        # make less revenue given the stricter constraints. So if we suddenly make more revenue than (effectively) 
        # last iteration, we know something has done wrong.
        elif BSP.objVal < Theta[s].x - EPS:
            print("ERROR! Bad Theta Value! " + str(BSP.objVal) + " < " + Theta[s].x + " + " + str(EPS), s)

    iter += 1

    if numCuts == 0:
        # If we haven't added any cuts in the current iteration, we can concludee have reached the optimal solution and therefore we can break
        reachedOptimal = True
        print("No Cuts Added")
    

# Print details about the optimal solution
# For now, just print out the negative of the objVal.
# Negative because we've converted this problem to a minimum
# of the negative for use with the Dual
print("Optimal Solution: " + str(-BMP.objVal))