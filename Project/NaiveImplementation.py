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
import os

# ------ Import data ------
data_file = os.path.join(".", "Project", "testData.json")

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
examRooms = parsed_data["Rooms"]
Rooms = RoomManager()
for examRoom in examRooms:
    Rooms.add_room(examRoom)

# ------ Sets ------
# Some sets are already defined above
# Events (one course can have multiple exam (events))
Events = frozenset(r for r in sum((x.events() for x in courseManager.courses), []))

# -- Periods --

# Calculate number of days in exam period
NumDays = parsed_data["Periods"] // parsed_data["SlotsPerDay"]

# Set of days
Days = list(range(NumDays))

# Set of Periods in each day
Timeslots = list(range(parsed_data["SlotsPerDay"]))

# ------ Data ------
# -- Constraints --
constraints = constrManager

# -- Courses --
courses = courseManager

# -- Curricula --
curricula = curriculaManager

# -- Teachers --
teachers = parsed_data["Teachers"]

# -- Exam Distance --
primaryPrimaryDistance = parsed_data["PrimaryPrimaryDistance"]


print("\n\n------\nGurobi\n------")
# --- Define Model ---
m = Model("Uni Exams")


# ------ Variables ------
# X = 1 if event e is assigned to period p and room r, 0 else
X = {
    (e, d, t, r): m.addVar(vtype=GRB.BINARY)
    for e in Events
    for d in Days
    for t in Timeslots
    for r in Rooms
}

# Y = 1 if event e is assigned to day d and timeslot t, 0 else (auxiliary variable)
Y = {
    (e, d, t): m.addVar(vtype=GRB.BINARY)
    for e in Events
    for d in Days
    for t in Timeslots
}

# The ordinal (order) value of the period assigned to event e
H = {e: m.addVar(vtype=GRB.INTEGER) for e in Events}


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

# Constraint 1: Each event assigned to an available period and room
RoomRequest = {
    e: m.addConstr(
        quicksum(X[e, d, t, r] for t in Timeslots for d in Days for r in Rooms) == 1
    )
    for e in Events
}

# Constraint 2: At most one event can use a room at once
RoomOccupation = {
    (r, d, t): m.addConstr(quicksum(X[e, d, t] for e in Events))
    for r in Rooms
    for t in Timeslots
    for d in Days
}


HardConflicts = {m.addConstr()}


Precendences = {m.addConstr()}

Unavailabilities = {m.addConstr()}

# AssignEventToOnePeriod = {
#     (e, d, p): m.addConstr(quicksum(y[e, d, p] for d in Days for p in P) == 1)
#     for e in E
#     for d in Days
#     for p in P
# }

# OneEventPerRoom = {
#     (e, d, p, r): m.addConstr(quicksum(X[e, d, p, r] for e in E) == 1)
#     for d in Days
#     for p in P
#     for r in R
# }

# EventPrecedence = {(e1, e2): m.addConstr(H[e1] - H[e2] <= -1) for (e1, e2) in F}


# ------ Objective Function ------
# m.setObjective(0, GRB.MAXIMIZE)

# ------ Print output ------

# print("Objective Value:", m.ObjVal)
