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
from Period import Period
from Utils import concat

previous_time = time.time()

# ------ Import data ------
data_file = os.path.join(".", "Project", "data", "D1-1-16.json")

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

print("Data import:", time.time() - previous_time, "seconds")
previous_time = time.time()

# Weights of Soft Constraints
SC_PRIMARY_SECONDARY = 5
SC_SECONDARY_SECONDARY = 1
P_UNDESIRED_PERIOD = 10
P_NOT_PREFERED_ROOM = 2
P_UNDESIRED_ROOM = 5
DD_SAME_EXAMINATION = 15
DD_SAME_COURSE = 12
UD_PRIMARY_PRIMARY = 2
UD_PRIMARY_SECONDARY = 2

# ------ Sets ------
# Some sets are already defined above
# -- Events --
# (one course can have multiple exam (events))

# Get courses
courses: list[Course] = courseManager.get_courses()

# Lookup dictionary of events for a given course
CourseEvents: Dict[Course, Event] = {
    course: [event for event in course.get_events()] for course in courses
}

# Extract exams from CourseList and store in one frozenset
Events: Set[Event] = frozenset(concat(CourseEvents.values()))

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
F = set()
for course in CourseEvents:
    if len(course.get_events()) > 1 and course.get_exam_type() == "WrittenAndOral":
        F.add(tuple(course.get_events()))

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


# The set of event pairs with a directed soft distance constraint.
# The ONLY pairs of events that can have such a constraint are (written, oral)
# pairs from a single course where the oral exam does NOT require a room
DPDirected = set()
# The set of event pairs with an undirected soft distance constraint.
# If (e1, e2) in DPUndirected, then (e2, e1) is also.
DPUndirected = set()
for c in courses:
    if (
        c.get_exam_type() == "WrittenAndOral"
        and not c.written_oral_specs["RoomForOral"]
        and c.min_distance_between_exams is not None
    ):
        # find the actual written and oral events
        writtenEvent = None
        oralEvent = None
        for event in Events:
            if event.course is not c:
                continue
            if event.event_type == "Written":
                writtenEvent = event
            elif event.event_type == "Oral":
                oralEvent = event
            else:
                raise Exception("course-event mismatch on course ", c)
            # We might be able to exit early
            if writtenEvent is not None and oralEvent is not None:
                break
        DPDirected.add((writtenEvent, oralEvent))
    elif c.num_of_exams > 1 and c.min_distance_between_exams is not None:
        course_events = [e for e in Events if e.course is c]
        assert len(course_events) == c.num_of_exams
        DPUndirected.add(tuple(course_events))
        course_events.reverse()
        DPUndirected.add(tuple(course_events))


print("Calculating Sets:", time.time() - previous_time, "seconds")
previous_time = time.time()

# ------ Data ------
# -- Teachers --
teachers = parsed_data["Teachers"]

# -- Exam Distance --
primaryPrimaryDistance = parsed_data["PrimaryPrimaryDistance"]


print("------\nGurobi\n------")
room_constraints = constrManager.get_room_period_constraints()
event_constraints = constrManager.get_event_period_constraints()
period_constraints = constrManager.get_period_constraints()

# Soft constraint undesired period violation cost for event e to be assigned to
# period p
UndesiredPeriodCost = {}
for e in Events:
    undesired_periods = [
        c.get_period()
        for c in constrManager.get_undesired_event_period_constraints()
        if c.get_course_name() == e.course_name
    ]
    for p in PA[e]:
        if p in undesired_periods:
            UndesiredPeriodCost[e, p] = P_UNDESIRED_PERIOD
        else:
            UndesiredPeriodCost[e, p] = 0

# Soft constraint undesired room violation cost for event e to be assigned to
# period p
UndesiredRoomCost = {}
for e in Events:
    undesired_rooms = [
        c.get_room()
        for c in constrManager.get_undesired_event_room_constraints()
        if c.get_course_name == e.course_name
    ]
    for r in RA[e]:
        if r in undesired_rooms:
            UndesiredRoomCost[e, r] = P_UNDESIRED_ROOM
        else:
            UndesiredRoomCost[e, r] = 0

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
H = {
    e: m.addVar(vtype=GRB.INTEGER, ub=Periods[-1].get_ordinal_value(slots_per_day))
    for e in Events
}

SPS = {(e, p): m.addVar(vtype=GRB.INTEGER) for e in Events for p in Periods}
SSS = {(e, p): m.addVar(vtype=GRB.INTEGER) for e in Events for p in Periods}

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
# M: Number of elements (rooms maybe - confirm with Michael) in the overlapping roomconcat
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

# Constraint 7a. Limit only 1 sum p of Y[e, p] to be turned on for each event
oneP = {m.addConstr(quicksum(Y[e, p] for p in PA[e]) == 1) for e in Events}

# Soft Constraints

# ------ Objective Function ------
m.setObjective(
    # Cost S1
    SC_PRIMARY_SECONDARY * quicksum(SPS[e, p] for e in Events for p in PA[e])
    + SC_SECONDARY_SECONDARY * quicksum(SSS[e, p] for e in Events for p in PA[e])
    # Cost S2
    + quicksum(UndesiredPeriodCost[e, p] * Y[e, p] for e in Events for p in PA[e])
    + quicksum(
        UndesiredRoomCost[e, r] * X[e, p, r]
        for e in Events
        for p in PA[e]
        for r in RA[e]
    )
    # Cost S3
)


print("Define Gurobi Model:", time.time() - previous_time, "seconds")
previous_time = time.time()
# ------ Optimise -------
m.optimize()
print("Optimise Gurobi Model:", time.time() - previous_time, "seconds")
previous_time = time.time()

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
