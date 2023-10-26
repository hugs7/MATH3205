"""
Prints the names of the problem sets in the form of a latex table
"""


import json
import os
from typing import List

class ProblemSet:
    def __init__(self, problemSetName):
        self.problemSetName = problemSetName
        self.ourObjectiveValue = None

        self.paperObjectiveValue = None

    def get_name(self):
        return self.problemSetName
    
    def get_our_objective_value(self):
        return self.ourObjectiveValue
    
    def get_paper_objective_value(self):
        return self.paperObjectiveValue
    
    def set_our_objective_value(self, objectiveValue):
        self.ourObjectiveValue = objectiveValue

    def set_paper_objective_value(self, objectiveValue):
        self.paperObjectiveValue = objectiveValue

ourSolutionPath = os.path.join(".", "Project", "OurSolutions")
paperSolutionPath = os.path.join(".", "Project", "Solutions", "BestSolutions")

problemSets: List[ProblemSet] = []

for filename in os.listdir(ourSolutionPath):
    if os.path.isfile(os.path.join(ourSolutionPath, filename)):
        problemSetName = filename.split(".")[0]
        problemSetName = filename.split("_")[0]
        problemSet = ProblemSet(problemSetName)
        problemSets.append(problemSet)

# Get objective value from our solutions
for problemSet in problemSets:
    with open(os.path.join(ourSolutionPath, problemSet.get_name() + "_sol.json")) as f:
        data = json.load(f)
        ourObjVal = data["Cost"]
        problemSet.set_our_objective_value(ourObjVal)


# Get objective value from paper solutions
for problemSet in problemSets:
    with open(os.path.join(paperSolutionPath, "sol_" + problemSet.get_name() + ".json")) as f:
        data = json.load(f)
        paperObjVal = data["Cost"]
        problemSet.set_paper_objective_value(paperObjVal)


# Print as latex table
print("\\begin{table}[htb]")
print("    \\centering")
print("    \\begin{tabular}{|l|r|r|}")
print("        \\hline")
print("        \\textbf{Problem Set} & \\textbf{Our Objective (Benders)} & \\textbf{Paper's Objective} \\\\")
print("        \\hline")
for problemSet in problemSets:
    print(f"        {problemSet.get_name()} & {problemSet.get_our_objective_value()} & {problemSet.get_paper_objective_value()} \\\\")
print("        \\hline")
print("    \\end{tabular}")
print("    \\caption{Comparison of our objective value and the paper's objective value}")
print("    \\label{tab:comparison}")
print("\\end{table}")
