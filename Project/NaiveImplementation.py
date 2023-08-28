"""
This file defines a naive implementation for the Exam timetabling problem

Hugo Burton
27/08/2023
"""

from gurobipy import Model, quicksum, GRB
import json  # For importing the data as JSON format

from Room import RoomManager
from Constraint import ConstraintManager
from Course import CourseManager
from Curriculum import CurriculaManager

# ------ Import data ------
data_file = ".\\Project\\testData.json"

with open(data_file, "r") as json_file:
    json_data = json_file.read()

parsed_data = json.loads(json_data)

# ------ Separate out data ------

# Exam schedule constraints
constrs = parsed_data["Constraints"]
constrManager = ConstraintManager()
for constraint in constrs:
    constrManager.add_constraint(constraint)

# Courses
crces = parsed_data["Courses"]
courseManager = CourseManager()
for course in crces:
    courseManager.add_course(course)

# Curricula
curicla = parsed_data["Curricula"]
curriculaManager = CurriculaManager()
for curriculum in curicla:
    curriculaManager.add_curriculum(curriculum)


# Rooms
rooms = parsed_data["Rooms"]
roomManager = RoomManager()
for room in rooms:
    roomManager.add_room(room)

print("\n\n------\nGurobi\n------")
# --- Define Model ---
m = Model("Uni Exams")

# ------ Sets ------


# ------ Data ------
# Constraints
constraints = constrManager

# Courses
courses = courseManager

# Curricula
curricula = curriculaManager

# Teachers
teachers = parsed_data["Teachers"]

# Time Periods
periods = parsed_data["Periods"]

# Time slots
slotsPerDay = parsed_data["SlotsPerDay"]

# Exam Distance
primaryPrimaryDistance = parsed_data["PrimaryPrimaryDistance"]

# Rooms
rooms = roomManager

# ------ Variables ------
X = {(e, p, r): m.addVar(vtype=GRB.BINARY) for e in E for p in P for r in R}


# ------ Objective Function ------
# m.setObjective(0, GRB.MAXIMIZE)

# ------ Print output ------

# print("Objective Value:", m.ObjVal)
