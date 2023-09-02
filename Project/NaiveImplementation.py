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

# Cannot add any more rooms after this
Rooms.construct_composite_map()

# ------ Sets ------
# Some sets are already defined above
# -- Events --
# (one course can have multiple exam (events))
Events = frozenset(r for r in sum((x.events() for x in courseManager.courses), []))

# -- Periods --
# Redefine set of periods into days and timeslots
# Calculate number of days in exam period
NumDays = parsed_data["Periods"] // parsed_data["SlotsPerDay"]

# Set of days
Days = list(range(NumDays))

# Set of Periods in each day
Timeslots = list(range(parsed_data["SlotsPerDay"]))

# Set of composite rooms
CompositeRooms = Rooms.get_composite_rooms()

# -- Room Equivalence Class --
K = {}

# The set of overlapping rooms of composite room
# Indexed by rc
R0 = {}

# Dictionary mapping events to a set of rooms in which it can be held
RA = {}
for e in Events:
    if e.num_rooms == 0:
        RA[e] = set((Rooms.get_dummy_room(),))
    elif e.num_rooms == 1:
        RA[e] = set(r for r in Rooms.get_single_rooms() if r.get_type() == e.room_type)
    else:
        RA[e] = set(
            r
            for r in Rooms.get_composite_rooms()
            if len(r.get_members()) >= e.num_rooms
            and next(iter(Rooms.composite_map[r])).get_type() == e.room_type
        )

# The set of available room equivalence classes for event e
KE = {}

# F = the set of examination pairs with precendence constraints
F = {}

# dictionary mapping events e to the set of events in H3 hard conflict with e
HC = {}  # type is dict[Event, Frozenset(Event)]
for e in Events:
    primary_curricula_courses = set(
        sum(
            (
                c.primary_courses
                for c in curriculaManager.curricula
                if e in c.primary_courses
            ),
            [],
        )
    )
    conflict_set = set(sum((c.events() for c in primary_curricula_courses), []))
    teacher_courses = set(
        c for c in courseManager.courses if c.teacher == e.course_teacher
    )
    conflict_set |= set(sum((c.events() for c in teacher_courses), []))
    HC[e] = frozenset(conflict_set)

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
# for constraint in constrManager:
#     print(constraint.type)
#     print(constraint.level)
#     print(constraint.exam)

room_constraints = constrManager.get_room_constraints()
event_constraints = constrManager.get_event_constraints()
period_constraints = constrManager.get_period_constraints()
course_list = constrManager.get_course_list()

# Constraint 1: Each event assigned to an available period and room.
RoomRequest = {
    e: m.addConstr(
        quicksum(X[e, d, t, r] for t in Timeslots for d in Days for r in Rooms) == 1
    )
    for e in Events
}

# Constraint 2: At most one event can use a room at once.
RoomOccupation = {
    (r, d, t): m.addConstr(quicksum(X[e, d, t] for e in Events) <= 1)
    for r in Rooms
    for t in Timeslots
    for d in Days
}

# Constraint 3: Two events must have different periods if they are in hard conflict
# Occurs in the following cases:
#   - They are part of the same primary curriculum
#   - They have the same teacher
# M: Number of elements in the overlapping rooms sum
M = 1
# rc is room-composite   - Rooms that are composite
# ro is room-overlapping - Rooms that overlap in a composite room
HardConflicts = {
    m.addConstr(
        M * quicksum(X[e, d, t, cr] for e in Events)
        + quicksum(X[e, d, t, ro] for e in Events for ro in R0[cr])
        <= M
    )
    for cr in CompositeRooms
    for d in Days
    for t in Timeslots
}

# Constraint 4: Some events must precede other events (hard constraint).
Precendences = {m.addConstr(H[e1] - H[e2] <= -1) for (e1, e2) in F}

# Constraint 5: Some rooms, day and timeslot configurations are unavailable.
Unavailabilities = {
    m.addConstr(M * Y[e, d, t] + quicksum(Y[e2, d, t] for e2 in HC[e]) <= M)
    for e in Events
    for d in Days
    for t in Timeslots
}

# Soft Constraints

# ------ Objective Function ------
# m.setObjective(0, GRB.MAXIMIZE)

# ------ Print output ------

# print("Objective Value:", m.ObjVal)
