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

# ------ Separate out data ------

parsed_data = json.loads(json_data)

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
# Events (one course can have multiple exam (events))
E = {}

# Periods
P = {}

# Rooms
R = {}

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
rooms = parsed_data["Rooms"]
roomManager = RoomManager()
for room in rooms:
    roomManager.add_room(room)

# Rooms
rooms = roomManager



print("\n\n------\nGurobi\n------")
# --- Define Model ---
m = Model("Uni Exams")

# ------ Sets ------
# Events (one course can have multiple exam (events))
E = {}

# Periods
NumDays = periods // slotsPerDay
Days = list(range(NumDays))

P = {}

# Rooms
R = {}


# ------ Variables ------
# X = 1 if event e is assigned to period p and room r, 0 else
X = {(e, d, p, r): m.addVar(vtype=GRB.BINARY) for e in E for d in Days for p in P for r in R}

# Y = 1 if event e is assigned to period p, 0 else (auxiliary variable)
Y = {(e, d, p): m.addVar(vtype=GRB.BINARY) for e in E for d in Days for p in P}

# The ordinal (order) value of the period assigned to event e
H = {e: m.addVar(vtype=GRB.INTEGER) for e in E}

# ------ Constraints ------
for constraint in constrManager:
    print(constraint.type)
    print(constraint.level)
    print(constraint.exam)

room_constraints = constrManager.get_room_constraints()
event_constraints = constrManager.get_event_constraints()
period_constraints = constrManager.get_period_constraints()
course_list = constrManager.get_course_list()
breakpoint()

AssignEventToOnePeriod = {(e,d,p):
    m.addConstr(quicksum(y[e,d,p] for d in Days for p in P)== 1)
    for e in E}

OneEventPerRoom = {(e,d,p,r):
    m.addConstr(quicksum(X[e,d,p,r] for e in E)==1)
    for d in Days for p in P for r in R
    }

EventPrecedence = {(e1,e2):
    m.addConstr(H[e1]-H[e2] <= -1) for (e1,e2) in F
    }

# ------ Objective Function ------
# m.setObjective(0, GRB.MAXIMIZE)

# ------ Print output ------

# print("Objective Value:", m.ObjVal)
