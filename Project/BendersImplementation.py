"""
This file defines a naive implementation for the Exam timetabling problem

Hugo Burton, Anna Henderson, Mitchell Holt
27/08/2023
"""

import time
from gurobipy import Model, quicksum, GRB
import json  # For importing the data as JSON format
import os
from typing import Dict, List, Set, Tuple, Union
from Examination import Examination

# Custom Imports
from Room import RoomManager, Room
from Constraint import (
    ConstraintManager,
    EventPeriodConstraint,
    EventRoomConstraint,
    RoomPeriodConstraint,
)
from Course import CourseManager, Course
from Event import Event
from Curriculum import CurriculaManager, Curriculum
from Period import Period
import Constants as const

previous_time = time.time()

# ------ Import data ------
data_file = os.path.join(".", "Project", "data", "D1-3-16.json")

with open(data_file, "r") as json_file:
    json_data = json_file.read()

# ------ Parse data with JSON ------

parsed_data = json.loads(json_data)

# Timeslots per day
slots_per_day = parsed_data[const.SLOTS_PER_DAY]

# Primary Primary Distance
primary_primary_distance = parsed_data[const.PRIMARY_PRIMARY_DISTANCE]

# Exam schedule constraints
constrManager = ConstraintManager(slots_per_day)
for constraint in parsed_data[const.CONSTRAINTS]:
    constrManager.add_constraint(constraint)

# Courses
courseManager = CourseManager()
for course in parsed_data[const.COURSES]:
    courseManager.add_course(course)

# Curricula
curriculaManager = CurriculaManager()
for curriculum in parsed_data[const.CURRICULA]:
    curriculaManager.add_curriculum(curriculum)

# Rooms
examRooms = parsed_data[const.ROOMS]
Rooms = RoomManager()
for examRoom in examRooms:
    Rooms.add_room(examRoom)

# Cannot add any more rooms after this
Rooms.construct_composite_map()

dummy_room = Rooms.get_dummy_room()

# Problem Constraints (from data)

# Event Period Constraints
event_period_constraints = constrManager.get_event_period_constraints()
undesired_event_period_constraints = (
    constrManager.get_undesired_event_room_constraints()
)

# Room Period Constraints
room_period_constraints = constrManager.get_room_period_constraints()
undesired_room_period_constraints = (
    constrManager.get_undesired_room_period_constraints()
)
forbidden_room_period_constraints = (
    constrManager.get_forbidden_room_period_constraints()
)

# Event Room Constraint
event_room_constraints = constrManager.get_event_room_constraints()
undesired_event_room_constraints = constrManager.get_undesired_event_room_constraints()
forbidden_event_room_constraints = constrManager.get_forbidden_event_room_constraints()

# Period Constraints
period_constraints = constrManager.get_period_constraints()
undesired_period_constraints = constrManager.get_undesired_period_constraints()

# Forbidden period constraints (any event any room)
# Convert periods into day and timeslot tuples
forbidden_period_constraints: List[Period] = [
    period_constraint.get_period()
    for period_constraint in constrManager.get_forbidden_period_constraints()
]

print("Data import:", time.time() - previous_time, const.SECONDS)
previous_time = time.time()

# ------ Sets ------
# Some sets are already defined above
# -- Events --
# (one course can have multiple examinations)
# an exmamination can have multiple events

# Get courses
Courses: List[Course] = courseManager.get_courses()

# Lookup dictionary of examinations for a given course
CourseExaminations: Dict[Course, List[Examination]] = {
    course: [examination for examination in course.get_examinations()]
    for course in Courses
}

# Extract examinations from CourseList and store in one frozenset
Examinations: Set[Examination] = set()
for course in Courses:
    examinations = course.get_examinations()
    for examination in examinations:
        Examinations.add(examination)

# Extract Events from the set of Examinations and store as list
Events: Set[Event] = set(
    [event for examination in Examinations for event in examination.get_events()]
)

# Lookup dictionary of events for a given course
CourseEvents: Dict[Course, List[Event]] = {
    course: [
        event for examination in Examinations for event in examination.get_events()
    ]
    for course in Courses
}

# ------- Constraints -------

# Forbidden event period constraints. Dictionary of [CourseEvent: Period]
forbidden_event_period_constraints: Dict[Event, List[Period]] = {}

# Initialise dictionary with an empty list for each event
for event in Events:
    event: Event
    forbidden_event_period_constraints[event] = []

# Iterate through forbidden_event_period_constraints and add to the right list as required
for event_period_constraint in constrManager.get_forbidden_event_period_constraints():
    # Period that the EventPeriodConstraint correspondds to
    period = event_period_constraint.get_period()

    # Corresponding Course
    course_name = event_period_constraint.get_course_name()
    course = courseManager.get_course_by_name(course_name)
    course_exams = course.get_examinations()

    # Loop over the exams in the course
    for exam in course_exams:
        # Check the exam number matches the constraint
        if exam.get_index() != event_period_constraint.get_exam_ordinal():
            continue

        if event_period_constraint.get_part() == const.WRITTEN:
            event = exam.get_written_event()
        elif event_period_constraint.get_part() == const.ORAL:
            event = exam.get_oral_event()

        forbidden_event_period_constraints[event].append(period)

# ----- Periods -----
# Redefine set of periods into days and timeslots
# Calculate number of days in exam period
NumDays = parsed_data[const.PERIODS] // slots_per_day

# Set of days
Days = list(range(NumDays))

# Set of Timeslots in each day
Timeslots = list(range(slots_per_day))

# Set of periods each day
Periods = [
    Period(day, timeslot, slots_per_day) for day in Days for timeslot in Timeslots
]

# Set of composite rooms (R^C) in paper)
CompositeRooms: List[Room] = Rooms.get_composite_rooms()

# Maximum number of members in composite rooms by the type of room
max_members_by_room_type: Dict[str, int] = Rooms.get_max_members_dict()

# -- Room Equivalence Class --
# TODO Yet to determine what this is
K = {}

# The set of overlapping rooms of composite room
# Indexed by rc
R0 = Rooms.get_overlapping_rooms()

# -- Period Availabilities (P_e in paper) --
# Set of periods available for event e
PA: Dict[Event, List[Period]] = {}
for event in Events:
    PA[event] = []

    for period in Periods:
        if period in forbidden_period_constraints:
            continue

        if period in forbidden_event_period_constraints[event]:
            continue

        PA[event].append(period)

# -- Room availabilities --
# Dictionary mapping events to a set of rooms in which it can be held
# R_e in paper
RA: Dict[Event, List[Room]] = {}

available_types: Dict[str, List[str]] = {}
available_types[const.DUMMY] = [const.DUMMY]
available_types[const.SMALL] = [const.SMALL, const.MEDIUM, const.LARGE]
available_types[const.MEDIUM] = [const.MEDIUM, const.LARGE]
available_types[const.LARGE] = [const.LARGE]
available_types[const.COMPOSITE] = [const.COMPOSITE]

inverse_room_types: Dict[str, str] = {}
inverse_room_types[const.SMALL] = [const.SMALL]
inverse_room_types[const.MEDIUM] = [const.SMALL, const.MEDIUM]
inverse_room_types[const.LARGE] = [const.SMALL, const.MEDIUM, const.LARGE]

for event in Events:
    if event.get_num_rooms() == 0:
        # No room required. Set of dummy room
        RA[event] = {dummy_room}
    elif event.get_num_rooms() == 1:
        # Only a single room required
        # Get the set of rooms which are single and are of the right type

        room_set = set()
        for r in Rooms.get_single_rooms():
            if r.get_type() in available_types.get(event.get_room_type()):
                room_set.add(r)

        RA[event] = room_set
    else:
        # Composite Room required for this event
        # Get the set of rooms which are single and are of the right type

        room_set = set()
        for r in Rooms.get_composite_rooms():
            adjacent_rooms: List[Room] = Rooms.composite_map[r]

            if (
                len(r.get_members()) == event.get_num_rooms()
                and adjacent_rooms[0].get_type() == event.get_room_type()
            ):
                room_set.add(r)

        RA[event] = room_set

# The set of available room equivalence classes for event e
# K_e in paper
# TODO Yet to determine what this is
KE = {}

# F = the set of examination pairs with precendence constraints.
# But actually we use the event instead
# This occurs if they are written and oral parts of the same examination
# and they are part of two consecutive examinations of the same course

F: Set[Tuple[Event, Event]] = set()
# for examination in Examinations:
#     examination: Examination
#     corresponding_course: Course = examination.get_course()

#     if not corresponding_course.is_written_and_oral():
#         continue

#     F.add((examination.get_written_event(), examination.get_oral_event()))


# dictionary mapping events e to the set of events in H3 hard conflict with e
# HC_e in paper
HC: Dict[Event, Set[Event]] = {}

# Initialise empty list for every event
for e in Events:
    HC[e] = set()

for curriculum in curriculaManager.get_curricula():
    curriculum: Curriculum

    curriculum_events_by_teacher: Dict[str, List[Event]] = {}

    # Get all the primary events that are part of this curriculum and taught by the same teacher
    for course_name in curriculum.get_primary_course_names():
        course: Course = courseManager.get_course_by_name(course_name)

        course_teacher = course.get_teacher()

        # Get the set of events for this course
        course_events: List[Event] = CourseEvents.get(course)

        if course_teacher not in curriculum_events_by_teacher.keys():
            curriculum_events_by_teacher[course_teacher] = []

        curriculum_events_by_teacher[course_teacher].extend(course_events)

    for course_name in curriculum.get_primary_course_names():
        course: Course = courseManager.get_course_by_name(course_name)

        course_teacher = course.get_teacher()

        # Get the set of events for this course
        course_events: List[Event] = CourseEvents.get(course)

        for event in course_events:
            for curriculum_event in curriculum_events_by_teacher[course_teacher]:
                if event == curriculum_event:
                    continue
                HC[event].add(curriculum_event)


# The set of event pairs with a directed soft distance constraint. Occurs when
# 1. Written and Oral events of the same examination
#   minimum and maximum distance
# 2. Same course with multiple examinations. One exam is consecutive which removes symmetry
# in the problem. Placed between the first event of each examination if it is a multi-part exam
DPDirected: Set[Tuple[Event, Event]] = set()

# DP^{E} in paper
# Examination Event Pairs of the same course.
# This only applies to the first examination event if there are multiple
# Setting this here as the loop is present and is convenient.
DPSameCourse: Set[Tuple[Event, Event]] = set()

# DP^{WO}
# WO Event Parts of the same examination
# Setting this here as the loop is present and is convenient.
# Should contain events only from WRITTEN_AND_ORAL courses
DPWrittenOral: Set[Tuple[Event, Event]] = set()


# Written and Oral Events of the same examination
for examination in Examinations:
    examination: Examination
    corresponding_course: Course = examination.get_course()

    if corresponding_course.is_written_and_oral():
        # Safety check with written oral exam specs
        assert corresponding_course.get_written_oral_specs is not None

        # Find the actual written and oral events
        writtenEvent = examination.get_written_event()
        oralEvent = examination.get_oral_event()

        F.add((writtenEvent, oralEvent))
        DPDirected.add((writtenEvent, oralEvent))

        # Adding to DP^{WO} here as it is convenient
        DPWrittenOral.add((writtenEvent, oralEvent))

# Events belong to the same course
for course in Courses:
    course_examinations = CourseExaminations.get(course)

    # Consider first (written) event in each exam if it's a multi-parter
    for examination_a in course_examinations:
        for examination_b in course_examinations:
            examination_a: Examination
            examination_b: Examination
            if examination_a.__eq__(examination_b):
                continue

            # Don't add directed distance constraints if examination_a is to come after
            # examination_b
            if examination_a.get_index() > examination_b.get_index():
                continue

            event_a = examination_a.get_first_event()
            event_b = examination_b.get_first_event()

            F.add((event_a, event_b))
            DPDirected.add((event_a, event_b))

            #  DP^{E}
            DPSameCourse.add((event_a, event_b))

# DPUndirected - The set of event pairs with an undirected soft distance
# constraint. If (e1, e2) in DPUndirected, then (e2, e1) is also. Occurs when:
# 1. Same curriculum: if two courses belong to the same curriculum, there should be a
# minimum separation between the examinations. For two-event examinations, consider the
# first event only
DPUndirected: Set[Tuple[Event, Event]] = set()

# Loop over curriculums
for curricula in curriculaManager.get_curricula():
    curriucla_course_names = curricula.get_course_names()
    curricula_courses: List[Course] = []
    for course_name in curriucla_course_names:
        curricula_courses.append(courseManager.get_course_by_name(course_name))

    for course_a in curricula_courses:
        for course_b in curricula_courses:
            course_a: Course
            course_b: Course

            if course_a.__eq__(course_b):
                continue

            # Get minimum separation between exams
            course_a_min_dist = course_a.get_min_distance_between_exams()
            course_b_min_dist = course_b.get_min_distance_between_exams()

            course_a_examinations = CourseExaminations.get(course_a)
            course_b_examinations = CourseExaminations.get(course_b)

            # Consider first (written) event in each exam if it's a multi-parter
            # Add every combination of events for the two courses into the set.
            # No need to check if the examinations are equal as they won't be!
            # They will be from different courses
            for examination_a in course_a_examinations:
                for examination_b in course_b_examinations:
                    examination_a: Examination
                    examination_b: Examination

                    # Don't add directed distance constraints if examination_a is to come after
                    # examination_b

                    # Course a

                    if course_a.is_written() or course_a.is_written_and_oral():
                        event_a = examination_a.get_written_event()
                    elif course_a.is_oral():
                        event_a = examination_a.get_oral_event()

                    # Course b

                    if course_b.is_written() or course_b.is_written_and_oral():
                        event_b = examination_b.get_written_event()
                    elif course_b.is_oral():
                        event_b = examination_b.get_oral_event()

                    DPUndirected.add((event_a, event_b))

# $P1$ the set of all unordered pairs $s$ of events $s = \{e_1, e_2\}$
# for which there exists a curriculum with courses $c_1 \neq c_2$, not
# both primary courses, such that $e_1$ and $e_2$ are examination events
# for $c_1$ and $c_2$ respectively.

P1: Set[frozenset[Event, Event]] = set()

# Loop over curriculums
for curricula in curriculaManager.get_curricula():
    curriucla_course_names = curricula.get_course_names()
    curricula_courses: List[Course] = []
    for course_name in curriucla_course_names:
        curricula_courses.append(courseManager.get_course_by_name(course_name))

    course_exams: List[Examination] = []
    for course_a in curricula_courses:
        course_a: Course
        course_exams.extend([exam for exam in course_a.get_examinations()])

    for exam_a in course_exams:
        for exam_b in course_exams:
            exam_a: Examination
            exam_b: Examination

            exam_a_course: Course = exam_a.get_course()
            exam_b_course: Course = exam_b.get_course()

            if exam_a_course.__eq__(exam_b_course):
                continue

            if curricula.get_primary_course_names().__contains__(
                exam_a_course.get_course_name()
            ):
                continue

            events_a: List[Event] = exam_a.get_events()
            events_b: List[Event] = exam_b.get_events()

            for event_a in events_a:
                for event_b in events_b:
                    P1.add(frozenset([event_a, event_b]))

# P2R the set of all events with undesired room preferences
P2R: Set[Event] = set()
for event in Events:
    for event_period_constraint in undesired_event_period_constraints:
        course_name = event_period_constraint.get_course_name()
        exam_num = event_period_constraint.get_exam_ordinal()
        exam_part = event_period_constraint.get_part()

        course: Course = courseManager.get_course_by_name(course_name)
        exam: Examination = course.get_examination_by_index(exam_num)
        if exam_part == const.ORAL:
            event = exam.get_oral_event()
        elif exam_part == const.WRITTEN:
            event = exam.get_written_event()

        P2R.add(event)

# SCPS
# Dictionary mapping each primary event to the set of secondary
# courses in the same curriculum
SCPS = {}  # type is dict[Event, set(Event)]
for event in Events:
    event_course_name = event.get_course_name()

    overlapping_secondary_curriculum_courses = []

    for curriculum in curriculaManager.get_curricula():
        primary_course_names = curriculum.get_primary_course_names()
        secondary_course_names = curriculum.get_secondary_course_names()

        # If the course isn't primary, we shouldn't add any of the secondary courses
        if event_course_name not in primary_course_names:
            continue

        # This curricula containing the course in the primary section
        # Add all the courses from the secondary part of the course into the overlapping_secondary_curriculum
        for secondary_course_name in secondary_course_names:
            secondary_course = courseManager.get_course_by_name(secondary_course_name)
            if secondary_course not in overlapping_secondary_curriculum_courses:
                overlapping_secondary_curriculum_courses.append(secondary_course)

    # Now convert all these courses into events using the CourseEvent dictionary
    secondary_curricula_events = []
    for course in overlapping_secondary_curriculum_courses:
        secondary_curricula_events.extend(CourseEvents.get(course))

    SCPS[event] = set(secondary_curricula_events)

# SCSS
# Dictionary mapping each secondary event to the set of other
# secondary courses in the same curriculum
SCSS = {}  # tySe is dict[Event, set(Event)]
for event in Events:
    event_course = event.get_course()
    event_course_name = event_course.get_course_name()

    overlapping_secondary_curriculum_courses = []

    for curriculum in curriculaManager.get_curricula():
        secondary_course_names = curriculum.get_secondary_course_names()

        # If the course isn't secondary, we shouldn't add any of the secondary courses
        if event_course_name not in secondary_course_names:
            continue

        # This curricula containing the course in the secondary section
        # Add all the courses from the secondary part of the course into the overlapping_secondary_curriculum
        # Exclude the event_course_name
        for secondary_course_name in secondary_course_names:
            secondary_course = courseManager.get_course_by_name(secondary_course_name)
            if (
                secondary_course not in overlapping_secondary_curriculum_courses
                and secondary_course != event_course
            ):
                overlapping_secondary_curriculum_courses.append(secondary_course)

    # Now convert all these courses into events using the CourseEvent dictionary
    secondary_curricula_events = []
    for course in overlapping_secondary_curriculum_courses:
        secondary_curricula_events.extend(CourseEvents.get(course))

    SCSS[event] = set(secondary_curricula_events)

# The sets containing pairs to be considered for the S3 soft constraint
# constraints and objective contribution

# DPPrimaryPrimary is the set of event tuples from examinations of which their courses
# are found in the same primary curriculum
# This only applies to the first examination event if there are multiple
DPPrimaryPrimary: Set[Tuple[Event, Event]] = set()

# DPPrimaryPrimary is the set of event tuples from examinations of which
# the first corresponding course is primary and the second corresponding
# course is seconday
DPPrimarySecondary: Set[Tuple[Event, Event]] = set()

# Construct DPPrimaryPrimary and DPPrimarySecondary
for c in curriculaManager.get_curricula():
    primary_courses = [
        courseManager.get_course_by_name(name) for name in c.get_primary_course_names()
    ]

    secondary_courses = [
        courseManager.get_course_by_name(name)
        for name in c.get_secondary_course_names()
    ]

    for p1 in primary_courses:
        p1_examinations = p1.get_examinations()

        for p2 in primary_courses:
            if p1.__eq__(p2):
                continue

            p2_examinations = p2.get_examinations()

            for p1_exam in p1_examinations:
                for p2_exam in p2_examinations:
                    e1 = p1_exam.get_first_event()
                    e2 = p2_exam.get_first_event()

                    if (e1, e2) not in DPPrimaryPrimary:
                        DPPrimaryPrimary.add((e1, e2))

        for s in secondary_courses:
            s_examinations = s.get_examinations()

            for p1_exam in p1_examinations:
                for s_exam in s_examinations:
                    e1 = p1_exam.get_first_event()
                    e2 = s_exam.get_first_event()

                    if (e1, e2) not in DPPrimarySecondary:
                        DPPrimarySecondary.add((e1, e2))


# Soft constraint undesired period violation cost for event e to be assigned to
# period p
UndesiredPeriodCost = {}
undesired_periods = set(p.get_period() for p in period_constraints if p.is_undesired())
for e in Events:
    undesired_periods = [
        c.get_period()
        for c in constrManager.get_undesired_event_period_constraints()
        if c.get_course_name() == e.get_course_name()
    ]
    for p in PA[e]:
        if p in undesired_periods or p in undesired_periods:
            UndesiredPeriodCost[e, p] = const.P_UNDESIRED_PERIOD
        else:
            UndesiredPeriodCost[e, p] = 0

# Soft constraint undesired room violation cost for event e to be assigned to
# period p. \alpha in the paper
UndesiredRoomCost = {}
undesired_rooms: Dict[Event, List[Room]] = {}

for e in Events:
    undesired_rooms[e] = [
        event_room_constraint.get_room_name()
        for event_room_constraint in undesired_event_room_constraints
        if event_room_constraint.get_course_name() == e.get_course_name()
    ]

    for r in RA[e]:
        if r in undesired_rooms[e]:
            UndesiredRoomCost[e, r] = const.P_UNDESIRED_ROOM
        else:
            UndesiredRoomCost[e, r] = 0


print("Calculating Sets:", time.time() - previous_time, const.SECONDS)
previous_time = time.time()

# ------ Data ------
# -- Teachers --
teachers = parsed_data[const.TEACHERS]

# -- Exam Distance --
primaryPrimaryDistance = parsed_data[const.PRIMARY_PRIMARY_DISTANCE]


print(f"------\n{const.GUROBI}\n------")

# ------ Define Model ------

BMP = Model(const.UNIVERSITY_EXAMINATIONS)

# ------ Variables ------
# Y = 1 if event e is assigned to day d and timeslot t, 0 else (auxiliary variable)
Y = {(e, p): BMP.addVar(vtype=GRB.BINARY) for e in Events for p in Periods}

# The ordinal (order) value of the period assigned to event e
H = {e: BMP.addVar(vtype=GRB.INTEGER) for e in Events}

# Replacing cost of undesired rooms in the BMP objective function
S2R = {p: BMP.addVar(vtype=GRB.INTEGER) for p in Periods}

# Soft constraint counting variables. The paper claims that all of these may be
# relaxed to be continuous.
# S1
SPS = {(e, p): BMP.addVar(vtype=GRB.CONTINUOUS) for e in Events for p in Periods}
SSS = {(e, p): BMP.addVar(vtype=GRB.CONTINUOUS) for e in Events for p in Periods}

# S3
PMinE = {(e1, e2): BMP.addVar(vtype=GRB.CONTINUOUS) for (e1, e2) in DPSameCourse}
PMinWO = {(e1, e2): BMP.addVar(vtype=GRB.CONTINUOUS) for (e1, e2) in DPWrittenOral}
PMaxWO = {(e1, e2): BMP.addVar(vtype=GRB.CONTINUOUS) for (e1, e2) in DPWrittenOral}
PMinPP = {(e1, e2): BMP.addVar(vtype=GRB.CONTINUOUS) for (e1, e2) in DPPrimaryPrimary}
PMinPS = {(e1, e2): BMP.addVar(vtype=GRB.CONTINUOUS) for (e1, e2) in DPPrimarySecondary}

# Variables for S3 soft constraints
# Abs distances between assignment of e1 and e2
D_abs = {(e1, e2): BMP.addVar(vtype=GRB.INTEGER) for e1 in Events for e2 in Events}

# Actual distances between assignments of e1 and e2
D_actual = {
    (e1, e2): BMP.addVar(vtype=GRB.INTEGER, lb=-GRB.INFINITY)
    for e1 in Events
    for e2 in Events
}
# 1 if D_actual[e1, e2] is positive
G = {(e1, e2): BMP.addVar(vtype=GRB.BINARY) for e1 in Events for e2 in Events}

# Abs Val of D_actual[e1, e2] or Zero
D_actual_abs_1 = {
    (e1, e2): BMP.addVar(vtype=GRB.INTEGER) for e1 in Events for e2 in Events
}
# Abs value of D_actual[e1, e2] or Zero
D_actual_abs_2 = {
    (e1, e2): BMP.addVar(vtype=GRB.INTEGER) for e1 in Events for e2 in Events
}

# ------ Constraints ------

# Limits every event to be assigned exactly 1 period
OnePeriodPerEvent = {
    e: BMP.addConstr(quicksum(Y[e, p] for p in Periods) == 1) for e in Events
}

# Hard upper limit on the number of events assigned to a period
# Total number of rooms around campus
num_rooms: int = len(Rooms.get_single_rooms())

# Rooms available per period
rooms_available: Dict[Period, int] = {}

print(time.time())
# Rooms available by size per period
forbidden_rooms_by_period_and_type: Dict[
    Tuple[Period, Union[const.SMALL, const.MEDIUM, const.LARGE]], List[Room]
] = {}
undesired_rooms_by_period_and_type: Dict[
    Tuple[Period, Union[const.SMALL, const.MEDIUM, const.LARGE]], List[Room]
] = {}

for p in Periods:
    rooms_available[p]: int = num_rooms
    for forbidden_room_period_constraint in forbidden_room_period_constraints:
        if forbidden_room_period_constraint.get_period() == p:
            rooms_available[p] -= 1

    # For now just constrain number of events to number of rooms available in the period
    # regardless of type
    # BMP.addConstr(
    #     quicksum(e.get_num_rooms() * Y[e, p] for e in Events if e.get_num_rooms() > 0)
    #     <= rooms_available[p]
    # )

    # Number of rooms available by size per period
    # This will be handy for callback

    for room_type in const.ROOM_TYPES:
        # Initialise empty list for every period and room type
        forbidden_rooms_by_period_and_type[(p, room_type)] = []
        undesired_rooms_by_period_and_type[(p, room_type)] = []

        for forbidden_room_period_constraint in forbidden_room_period_constraints:
            forbidden_room_period_constraint: RoomPeriodConstraint

            room_period_constraint_period: Period = (
                forbidden_room_period_constraint.get_period()
            )
            level: str = forbidden_room_period_constraint.get_level()
            room_name: str = forbidden_room_period_constraint.get_room_name()
            room: Room = Rooms.get_room_by_name(room_name)

            if level != const.FORBIDDEN:
                continue

            if room_period_constraint_period != p:
                continue

            if room.get_type() != room_type:
                continue

            print("Adding forbidden room in period", p, room_type, room)

            forbidden_rooms_by_period_and_type[(p, room_type)].append(room)

            # Check if room is part of any composite rooms
            # If so, add the composite room to the forbidden list as well
            for composite_room in CompositeRooms:
                composite_room_members = composite_room.get_members()
                if room_name in composite_room_members:
                    forbidden_rooms_by_period_and_type[(p, room_type)].append(
                        composite_room
                    )

        for undesired_room_constraint in undesired_room_period_constraints:
            undesired_room_constraint: RoomPeriodConstraint

            room_period_constraint_period: Period = (
                undesired_room_constraint.get_period()
            )
            level: str = undesired_room_constraint.get_level()
            room_name: str = undesired_room_constraint.get_room_name()
            room: Room = Rooms.get_room_by_name(room_name)

            if level != const.UNDESIRED:
                continue

            if room_period_constraint_period != p:
                continue

            if room.get_type() != room_type:
                continue

            print("Adding undesired room in period", p, room_type, room_name)

            undesired_rooms_by_period_and_type[(p, room_type)].append(room_name)

# Number of available rooms by period, type of room, and number of joining members
# Excludes forbidden room_period constraints
# Number of joining members = 1 => single room
# Number of joining members > 1 => composite room
available_rooms_by_period_type_and_size: Dict[Tuple[Period, str, int], List[Room]] = {}
# Begin by assigning all periods to have the same number of available rooms
for period in Periods:
    for room_type in const.ROOM_TYPES:
        if max_members_by_room_type.get(room_type) == 0:
            continue

        for num_members in range(1, max_members_by_room_type[room_type] + 1):
            available_rooms_by_period_type_and_size[
                (period, room_type, num_members)
            ] = [
                room
                for room in Rooms.get_rooms_by_size_and_num_rooms(
                    room_type, num_members
                )
                if room not in forbidden_rooms_by_period_and_type[(period, room_type)]
            ]

# Constraint 4: Some events must precede other events (hard constraint).
Precendences = {(e1, e2): BMP.addConstr(H[e1] - H[e2] <= -1) for (e1, e2) in F}

# Constraint 5: Some rooms, day and timeslot configurations are unavailable.
Unavailabilities = {
    (e, p): BMP.addConstr(
        len(HC[e]) * Y[e, p] + quicksum(Y[e2, p] for e2 in HC[e]) <= len(HC[e])
    )
    for e in Events
    for p in PA[e]
}

# Prevent events scheduled when they aren't allowed. Alternative to constraint 5 atm
# seems to give much more correct objective value from testing so far.

# PeriodScheduling = {
#     (e, p): BMP.addConstr(Y[e, p] == 0)
#     for e in Events
#     for p in Periods
#     if p not in PA[e]
# }

# Constraint 7: Set values of H_e
setH = {
    e: BMP.addConstr(quicksum(p.get_ordinal_value() * Y[e, p] for p in PA[e]) == H[e])
    for e in Events
}

# Constraint 7a: Limit only 1 sum p of Y[e, p] to be turned on for each event
# oneP = {e: BMP.addConstr(quicksum(Y[e, p] for p in Periods) == 1) for e in Events}
# for p in PA[e]
# oneP = {e: m.addConstr(quicksum(Y[e, p] for p in PA[e]) == 1) for e in Events}

print("Hard Constraints defined", time.time())
# Soft Constraints

# Constraint 8 (S1): Soft Conflicts
SoftConflicts = {
    (e, p): BMP.addConstr(
        len({e2 for e2 in SCPS[e] if (e, e2) in DPDirected and p in PA[e2]}) * Y[e, p]
        + quicksum(Y[e2, p] for e2 in SCPS[e] if (e, e2) in DPDirected)
        <= SPS[e, p]
        + len({e2 for e2 in SCPS[e] if (e, e2) in DPDirected and p in PA[e2]})
    )
    for e in Events
    for p in PA[e]
}

# Constraint 9 (S2): Preferences
Preferences = {
    (e, p): BMP.addConstr(
        len({e2 for e2 in SCSS[e] if (e, e2) in DPDirected and p in PA[e2]}) * Y[e, p]
        + quicksum(Y[e2, p] for e2 in SCSS[e] if (e, e2) in DPDirected)
        <= SSS[e, p]
        + len({e2 for e2 in SCSS[e] if (e, e2) in DPDirected and p in PA[e2]})
    )
    for e in Events
    for p in PA[e]
}

# Constraint 10 (S3): DirectedDistances
Constraint10 = {
    (e1, e2): BMP.addConstr(D_abs[e1, e2] == H[e2] - H[e1]) for (e1, e2) in DPDirected
}

# Constraint 11: (S4): UndirectedDifferences
Constraint11 = {
    (e1, e2): BMP.addConstr(D_actual[e1, e2] == H[e2] - H[e1])
    for (e1, e2) in DPUndirected
}

# Constraint 12:
Constraint12 = {
    (e1, e2): BMP.addConstr(D_actual[e1, e2] <= len(Periods) * G[e1, e2])
    for (e1, e2) in DPUndirected
}

Constraint13 = {
    (e1, e2): BMP.addConstr(D_actual[e1, e2] >= -len(Periods) * (1 - G[e1, e2]))
    for (e1, e2) in DPUndirected
}

Constraint14 = {
    (e1, e2): BMP.addConstr(D_actual_abs_1[e1, e2] <= len(Periods) * G[e1, e2])
    for (e1, e2) in DPUndirected
}

Constraint15 = {
    (e1, e2): BMP.addConstr(D_actual_abs_1[e1, e2] >= -len(Periods) * G[e1, e2])
    for (e1, e2) in DPUndirected
}

Constraint16 = {
    (e1, e2): BMP.addConstr(
        D_actual_abs_1[e1, e2] <= D_actual[e1, e2] + len(Periods) * (1 - G[e1, e2])
    )
    for (e1, e2) in DPUndirected
}

Constraint17 = {
    (e1, e2): BMP.addConstr(
        D_actual_abs_1[e1, e2] >= D_actual[e1, e2] - len(Periods) * (1 - G[e1, e2])
    )
    for (e1, e2) in DPUndirected
}

Constraint18 = {
    (e1, e2): BMP.addConstr(
        D_actual_abs_2[e1, e2] == D_actual_abs_1[e1, e2] - D_actual[e1, e2]
    )
    for (e1, e2) in DPUndirected
}

Constraint19 = {
    (e1, e2): BMP.addConstr(
        D_abs[e1, e2] == D_actual_abs_1[e1, e2] + D_actual_abs_2[e1, e2]
    )
    for (e1, e2) in DPUndirected
}

Constraint20 = {}

for e1, e2 in DPSameCourse:
    e1_course: Course = e1.get_course()
    e2_course: Course = e2.get_course()

    exam_min_dist_1 = e1_course.get_min_distance_between_exams()
    exam_min_dist_2 = e2_course.get_min_distance_between_exams()
    exam_min_dist = max(exam_min_dist_1, exam_min_dist_2)

    Constraint20[(e1, e2)]: BMP.addConstr(
        PMinE[e1, e2] + D_abs[e1, e2] >= exam_min_dist
    )

Constraint21 = {}
Constraint22 = {}

for written_event, oral_event in DPWrittenOral:
    # written_event and oral_event are from the same course
    wo_course: Course = written_event.get_course()
    assert wo_course is not None

    written_oral_specs = wo_course.get_written_oral_specs()

    min_distance = written_oral_specs.get_min_distance()
    max_distance = written_oral_specs.get_max_distance()

    Constraint21[(written_event, oral_event)]: BMP.addConstr(
        PMinWO[written_event, oral_event] + D_abs[written_event, oral_event]
        >= min_distance
    )
    Constraint22[(written_event, oral_event)]: BMP.addConstr(
        D_abs[written_event, oral_event] - PMaxWO[written_event, oral_event]
        <= max_distance
    )

Constraint23 = {}
for e1, e2 in DPPrimaryPrimary:
    e1_course: Course = e1.get_course()
    e2_course: Course = e2.get_course()

    Constraint23[(e1, e2)]: BMP.addConstr(
        PMinPP[e1, e2] + D_abs[e1, e2] >= primary_primary_distance
    )

Constraint24 = {}
for e1, e2 in DPPrimarySecondary:
    e1_course: Course = e1.get_course()
    e2_course: Course = e2.get_course()

    Constraint24[(e1, e2)]: BMP.addConstr(PMinPS[e1, e2] + D_abs[e1, e2] >= 1)
print("Constraints defined", time.time())
# ------ Objective Function ------
BMP.setObjective(
    # Cost S1
    const.SC_PRIMARY_SECONDARY * quicksum(SPS[e, p] for e in Events for p in PA[e])
    + const.SC_SECONDARY_SECONDARY * quicksum(SSS[e, p] for e in Events for p in PA[e])
    # Cost S2
    + quicksum(UndesiredPeriodCost[e, p] * Y[e, p] for e in Events for p in PA[e])
    + quicksum(const.P_UNDESIRED_ROOM * S2R[p] for p in Periods)
    # + quicksum(
    #     UndesiredRoomCost[e, r] * X[e, p, r]
    #     for e in Events
    #     for p in PA[e]
    #     for r in RA[e]
    # )
    # Cost S3
    + const.DD_SAME_COURSE * quicksum(PMinE[e1, e2] for (e1, e2) in DPSameCourse)
    + const.DD_SAME_EXAMINATION
    * quicksum(PMinWO[e1, e2] + PMaxWO[e1, e2] for (e1, e2) in DPWrittenOral)
    + const.UD_PRIMARY_PRIMARY
    / 2  # divided by 2 because both undirected pairs exist
    * quicksum(PMinPP[e1, e2] for (e1, e2) in DPPrimaryPrimary)
    + const.UD_PRIMARY_SECONDARY
    * quicksum(PMinPS[e1, e2] for (e1, e2) in DPPrimarySecondary),
    GRB.MINIMIZE,
)

# ---- Define Subproblem

# Dictionary to store subproblem objective valujes (one for each period)
# _SolveBSP: Dict[Period, float] = {}

previous_time = time.time()
print("Defined Gurobi Model:", time.time() - previous_time, const.SECONDS)

reachedOptimal = False
iter = 0
BMP.setParam("OutputFlag", 1)

while not reachedOptimal:
    print("Iteration " + str(iter))
    # ------ Optimise -------
    BMP.optimize()
    print(
        f"Optimise Gurobi Model ({str(iter)}): {time.time() - previous_time} {const.SECONDS}"
    )
    previous_time = time.time()

    print("Master Problem Objective: " + str(BMP.objVal))
    print("------" * 10)

    numCuts = 0

    for p in Periods:
        # Sets

        # Set of events that are assigned to period p (from the master problem)
        EventsP = [e for e in Events if Y[e, p].x > 0.9]

        # Set of events assigned to period p requiring room with type room_type and # members num_rooms
        events_p_by_type_and_size: Dict[Tuple[str, int], List[Event]] = {}
        for room_type in const.ROOM_TYPES:
            for num_members in range(1, max_members_by_room_type[room_type] + 1):
                events_p_by_type_and_size[(room_type, num_members)] = [
                    e
                    for e in EventsP
                    if e.get_room_type() == room_type
                    and e.get_num_rooms() == num_members
                ]

        # Define Sub Problem
        BSP = Model("BSP for Period " + str(p))

        # Set output flag off/on
        BSP.setParam("OutputFlag", 1)

        # Variables in Subproblem

        # X = 1 if event e is assigned to period p and room r, 0 else
        X = {(e, r): BSP.addVar(vtype=GRB.BINARY) for e in EventsP for r in Rooms}

        # Undesired Room. 1 if event e is assigned to an undesired room
        # (only in this period), 0 else
        UR = {e: BSP.addVar(vtype=GRB.BINARY) for e in EventsP}

        # Subproblem objective function

        BSP.setObjective(
            quicksum(UR[e] for e in EventsP),
            GRB.MINIMIZE,
        )

        # Subproblem Constraints

        # Constraint 1: Each event assigned to an available period and exactly 1 room.
        RoomRequest = {
            e: BSP.addConstr(quicksum(X[e, r] for r in RA[e]) == 1) for e in EventsP
        }

        # Constraint 2: At most one event can use a room at once.
        RoomOccupation = {
            r: BSP.addConstr(quicksum(X[e, r] for e in EventsP) <= 1)
            for r in Rooms
            if r is not dummy_room
        }

        # Constraint 3: Two events must have different periods if they are in hard conflict
        # Occurs in the following cases:
        #   - They are part of the same primary curriculum
        #   - They have the same teacher
        # M: Number of elements in the overlapping roomconcat sum
        # rc is room-composite   - Rooms that are composite
        # ro is room-overlapping - Rooms that overlap in a composite room

        HardConflicts = {
            cr: BSP.addConstr(
                (len(R0[cr])) * quicksum(X[e, cr] for e in EventsP)
                + quicksum(X[e, ro] for e in EventsP for ro in R0[cr])
                <= (len(R0[cr]))
            )
            for cr in CompositeRooms
        }

        # Events can't be scheduled to a room if that room is forbidden for the event
        ForbiddenRooms = {
            (e, r): BSP.addConstr(X[e, r] == 0)
            for e in EventsP
            for r in Rooms  # should be without dummy
            if r not in RA[e] and r is not dummy_room
        }

        UndesiredRooms = {
            e: BSP.addConstr(
                UR[e] == quicksum(X[e, r] for r in Rooms if r in undesired_rooms[e])
            )
            for e in EventsP
        }

        # Constraint 6: Set values of Y_(e,p)
        # This is now implicitly handled in the subproblem
        # setY = {
        #     (e, p): BMP.addConstr(Y[e, p] - quicksum(X[e, r] for r in RA[e]) == 0)
        #     for e in Events
        #     for p in PA[e]
        # }

        BSP.optimize()

        # Check if BSP is infeasible. If it is, I need to add a feasability cut to prevent as many events
        # being allocated to this period

        if BSP.status == GRB.INFEASIBLE:
            print("Infeasible")
            # Subproblem was infeasible. Add feasability cut

            # Find number of events allocated to period p that request small rooms
            room_allocations: Dict[str, int] = {}
            for room_type in const.ROOM_TYPES:
                # Initialise allocations to 0 if not set already
                if room_allocations.get(room_type) is None:
                    room_allocations[room_type] = 0

                # Loop over events and add to allocations if event is allocated to room
                # ensuring to add the number of rooms for composite events.
                for e in EventsP:
                    # If the event was scheduled in this period
                    if Y[e, p].x > 0.9 and e.get_room_type() == room_type:
                        # Add the number of rooms required by the event.
                        room_allocations[room_type] += e.get_num_rooms()

            # Just remember that a room request of small can use larger rooms
            # but this doesn't apply to composite rooms
            # print("Num rooms available", rooms_available[p])

            for room_type in const.ROOM_TYPES:
                print(room_type)

                if max_members_by_room_type[room_type] == 0:
                    continue

                for num_members in range(1, max_members_by_room_type[room_type] + 1):
                    print(
                        available_rooms_by_period_type_and_size[
                            (period, room_type, num_members)
                        ]
                    )

                    # Limit the number of events allocated to period p of type room_type
                    # with num_members members
                    BMP.addConstr(
                        quicksum(
                            Y[e, p]
                            for e in events_p_by_type_and_size[(room_type, num_members)]
                        )
                        <= sum(
                            len(
                                available_rooms_by_period_type_and_size[
                                    (period, room_type_star, num_members)
                                ]
                            )
                            for room_type_star in inverse_room_types[room_type]
                        )
                    )
                print()

            numCuts += 1

        # Optimality cut
        iter += 1

        if numCuts == 0:
            # If we haven't added any cuts in the current iteration, we can concludee have reached the optimal solution and therefore we can break
            reachedOptimal = True
            print("No Cuts Added")

# ------ Print output ------

# for event in Events:
#     for period in Periods:
#         if Y[event, period].x > 0.9:
#             print(event, period, Y[event, period].x)

print("----")
print("\n\nFinal Objective Value:", BMP.ObjVal, "\n\n")

for d in Days:
    print("------" * 10 + "\nDay ", d)
    for p in Periods:
        if p.get_day() == d:
            # print(f"{' '*4}Period ", p)
            for e in Events:
                if Y[e, p].x > 0.9:
                    print(f"{' '*4} Period {p}: exam {e}")

print("------" * 10)
