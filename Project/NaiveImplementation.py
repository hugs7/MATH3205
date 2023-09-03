"""
This file defines a naive implementation for the Exam timetabling problem

Hugo Burton, Anna Henderson, Mitchell Holt
27/08/2023
"""

import time
from gurobipy import Model, quicksum, GRB
import json  # For importing the data as JSON format
import os
from typing import Dict, List, Set, Tuple

# Custom Imports
from Room import RoomManager
from Constraint import ConstraintManager
from Course import CourseManager, Course, Event
from Curriculum import CurriculaManager
from period import Period


# ------ Import data ------
data_file = os.path.join(".", "Project", "data", "D7-2-17.json")

with open(data_file, "r") as json_file:
    json_data = json_file.read()

# ------ Parse data with JSON ------

parsed_data = json.loads(json_data)

# Timeslots per day
slots_per_day = parsed_data["SlotsPerDay"]

# Exam schedule constraints
constrManager = ConstraintManager(slots_per_day)
for constraint in parsed_data["Constraints"]:
    constrManager.add_constraint(constraint)

# Courses
courseManager = CourseManager()
for course in parsed_data["Courses"]:
    courseManager.add_course(course)

# Curricula
curriculaManager = CurriculaManager()
for curriculum in parsed_data["Curricula"]:
    curriculaManager.add_curriculum(curriculum)

# Rooms
examRooms = parsed_data["Rooms"]
Rooms = RoomManager()
for examRoom in examRooms:
    Rooms.add_room(examRoom)

# Cannot add any more rooms after this
Rooms.construct_composite_map()

room_constraints = constrManager.get_room_period_constraints()

# Event period Constraints
event_constraints = constrManager.get_event_period_constraints()
period_constraints = constrManager.get_period_constraints()

# Forbidden period constraints (any event any room)
# Convert periods into day and timeslot tuples
forbidden_period_constraints: List[Period] = [
    period_constraint.get_period()
    for period_constraint in constrManager.get_forbidden_period_constraints()
]

# ------ Sets ------
# Some sets are already defined above
# -- Events --
# (one course can have multiple exam (events))

# Get courses
courses: list[Course] = courseManager.get_courses()

# Lookup dictionary of events for a given course
CourseEvents = {course: [event for event in course.get_events()] for course in courses}

# Extract exams from CourseList and store in one large list.
# Can make this a frozen set in the future, though it's nice as a list for now.
Events: List[Event] = []
# Iterate through the CourseEvents dictionary and extend the Events list
for event_list in CourseEvents.values():
    Events.extend(event_list)

# Forbidden event period constraints. Dictionary of [CourseEvent: Period]
forbidden_event_period_constraints: Dict[Event, List[Period]] = {}
# Prepopulate dictionary with an empty list for each event
for event in Events:
    forbidden_event_period_constraints[event] = []

# Iterate through forbidden_event_period_constraints and add to the right list as required
for event_period_constraint in constrManager.get_forbidden_event_period_constraints():
    course_name = event_period_constraint.get_course_name()
    course = courseManager.get_course_by_name(course_name)
    event = course.get_events()[event_period_constraint.get_exam_ordinal()]

    forbidden_event_period_constraints[event].append(
        event_period_constraint.get_period()
    )

# -- Periods --
# Redefine set of periods into days and timeslots
# Calculate number of days in exam period
NumDays = parsed_data["Periods"] // slots_per_day

# Set of days
Days = list(range(NumDays))

# Set of Timeslots in each day
Timeslots = list(range(slots_per_day))

# Set of periods each day
Periods = [Period(day, timeslot) for day in Days for timeslot in Timeslots]

# Set of composite rooms (R^C) in paper)
CompositeRooms = Rooms.get_composite_rooms()
# -- Room Equivalence Class --
K = {}

# The set of overlapping rooms of composite room
# Indexed by rc
R0 = Rooms.get_overlapping_rooms()

# -- Period Availabilities (P_e in paper) --
# Set of periods available for event e

PA = {
    event: [
        period
        for period in Periods
        if period not in forbidden_period_constraints
        and period not in forbidden_event_period_constraints[event]
    ]
    for event in Events
}

# -- Room availabilities --
# Dictionary mapping events to a set of rooms in which it can be held
RA = {}
for event in Events:
    if event.num_rooms == 0:
        RA[event] = set((Rooms.get_dummy_room(),))
    elif event.num_rooms == 1:
        RA[event] = set(
            r for r in Rooms.get_single_rooms() if r.get_type() == event.room_type
        )
    else:
        RA[event] = set(
            r
            for r in Rooms.get_composite_rooms()
            if len(r.get_members()) >= event.num_rooms
            and next(iter(Rooms.composite_map[r])).get_type() == event.room_type
        )

# The set of available room equivalence classes for event e
KE = {}

# F = the set of examination pairs with precendence constraints
F: Set[Tuple[Event, Event]] = {}
for e1 in Events:
    for e2 in Events:
        if e1 == e2:
            continue

        e1_period_availabilities = PA[e1]
        e2_period_availabilities = PA[e2]

        if min(e2_period_availabilities) > max(e1_period_availabilities):
            # e1 must preceed e2
            F.add((e1, e2))
print("F", F)

# dictionary mapping events e to the set of events in H3 hard conflict with e
HC = {}  # type is dict[Event, Frozenset(Event)]
for event in Events:
    event_course = event.get_course()
    event_course_name = event_course.get_course_name()
    event_course_teacher = event_course.get_teacher()

    overlapping_primary_curriculum_courses = []

    for curriculum in curriculaManager.get_curricula():
        primary_course_names = curriculum.get_primary_course_names()
        if event_course_name not in primary_course_names:
            continue

        # This is the curricula contiaing the course
        # Add all the courses from here into the overlapping_primary_curriculum
        for primary_course_name in primary_course_names:
            primary_course = courseManager.get_course_by_name(primary_course_name)
            if primary_course not in overlapping_primary_curriculum_courses:
                overlapping_primary_curriculum_courses.append(primary_course)

    # Now convert all these courses into events using the CourseEvent dictionary
    primary_curricula_events = []
    for course in overlapping_primary_curriculum_courses:
        primary_curricula_events.extend(CourseEvents.get(course))

    # Find Teachers teaching the same course
    same_teacher_courses: List[Course] = []
    for course in courseManager.get_courses():
        if course.get_teacher() == event_course_teacher:
            same_teacher_courses.append(course)

    # Now convert all those same teacher courses to events
    same_teacher_events = []
    for course in same_teacher_courses:
        same_teacher_events.extend(CourseEvents.get(course))

    conflict_set = set(primary_curricula_events).union(set(same_teacher_events))

    HC[event] = conflict_set

# ------ Data ------

# -- Teachers --
teachers = parsed_data["Teachers"]

# -- Exam Distance --
primaryPrimaryDistance = parsed_data["PrimaryPrimaryDistance"]


print("------\nGurobi\n------")
room_constraints = constrManager.get_room_period_constraints()
event_constraints = constrManager.get_event_period_constraints()
period_constraints = constrManager.get_period_constraints()

# --- Define Model ---
m = Model("Uni Exams")


# ------ Variables ------
# X = 1 if event e is assigned to period p and room r, 0 else
X = {
    (e, p, r): m.addVar(vtype=GRB.BINARY)
    for e in Events
    for p in Periods
    for r in Rooms
}

# Y = 1 if event e is assigned to day d and timeslot t, 0 else (auxiliary variable)
Y = {(e, p): m.addVar(vtype=GRB.BINARY) for e in Events for p in Periods}

# The ordinal (order) value of the period assigned to event e
H = {e: m.addVar(vtype=GRB.INTEGER) for e in Events}


# ------ Constraints ------

# Constraint 1: Each event assigned to an available period and room.
RoomRequest = {
    e: m.addConstr(quicksum(X[e, p, r] for p in Periods for r in Rooms) == 1)
    for e in Events
}

# Constraint 2: At most one event can use a room at once.
RoomOccupation = {
    (r, p): m.addConstr(quicksum(X[e, p, r] for e in Events) <= 1)
    for r in Rooms
    for p in Periods
}

# Constraint 3: Two events must have different periods if they are in hard conflict
# Occurs in the following cases:
#   - They are part of the same primary curriculum
#   - They have the same teacher
# M: Number of elements (rooms maybe - confirm with Michael) in the overlapping rooms sum
# rc is room-composite   - Rooms that are composite
# ro is room-overlapping - Rooms that overlap in a composite room

HardConflicts = {
    (cr, p): m.addConstr(
        len(R0[cr]) * quicksum(X[e, p, cr] for e in Events)
        + quicksum(X[e, p, ro] for e in Events for ro in R0[cr])
        <= len(R0[cr])
    )
    for cr in CompositeRooms
    for p in Periods
}

# Constraint 4: Some events must precede other events (hard constraint).
Precendences = {(e1, e2): m.addConstr(H[e1] - H[e2] <= -1) for (e1, e2) in F}

# Constraint 5: Some rooms, day and timeslot configurations are unavailable.
Unavailabilities = {
    (e, p): m.addConstr(
        len(HC[e]) * Y[e, p] + quicksum(Y[e2, p] for e2 in HC[e]) <= len(HC[e])
    )
    for e in Events
    for p in PA[e]
}

# Constraint 6: Set values of Y_(e,p)
setY = {
    m.addConstr(Y[e, p] - quicksum(X[e, p, r] for r in RA[e]) == 0)
    for e in Events
    for p in PA[e]
}

# Constraint 7: Set values of H_e
setH = {
    m.addConstr(
        quicksum(p.get_ordinal_value(slots_per_day) * Y[e, p] for p in PA[e]) == H[e]
    )
    for e in Events
}

# Soft Constraints

# ------ Objective Function ------
# m.setObjective(0, GRB.MAXIMIZE)

# ------ Optimise -------
g_start_time = time.time()
m.optimize()
g_finish_time = time.time()

gurobi_time = g_finish_time - g_start_time
print("Time to optimise:", gurobi_time, "seconds")

# ------ Print output ------

print("Objective Value:", m.ObjVal)

for p in Periods:
    for e in Events:
        for r in Rooms:
            if X[e, p, r].x > 0.9:
                print(f"Day {p.get_day()}")
                print(f"  Timeslot {p.get_timeslot()}")
                print(f"    Exam {e} in room {r}")
                print()
