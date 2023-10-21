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
import Utils as utils
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


def solve(instance_name: str) -> None:
    print("---------------- Instance: ", instance_name, "----------------")
    previous_time = time.time()
    data_file = os.path.join(".", "Project", "data", instance_name)

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

    # Extract Events from the set of Examinations
    Events: Set[Event] = {
        event for examination in Examinations for event in examination.get_events()
    }

    # Lookup dictionary of events for a given course
    CourseEvents: Dict[Course, List[Event]] = {
        course: [
            event
            for examination in Examinations
            if examination.get_course() == course
            for event in examination.get_events()
        ]
        for course in Courses
    }

    # ------- Constraints -------

    # Forbidden event period constraints. Dictionary of [CourseEvent: Period]
    forbidden_event_period_constraints: Dict[Event, List[Period]] = {}

    # Initialise dictionary with an empty list for each event
    for event in Events:
        forbidden_event_period_constraints[event] = []

    # Iterate through forbidden_event_period_constraints and add to the right list as required
    for (
        event_period_constraint
    ) in constrManager.get_forbidden_event_period_constraints():
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
    CompositeRooms = Rooms.get_composite_rooms()

    # -- Room Equivalence Class --
    # TODO Yet to determine what this is
    K = {}

    # The set of overlapping rooms of composite room
    # Indexed by rc

    # -- Period Availabilities (P_e in paper) --
    # Set of periods available for event e
    PA: Dict[Event, Set[Period]] = {
        event: {
            p
            for p in Periods
            if p not in forbidden_period_constraints
            and p not in forbidden_event_period_constraints[event]
        }
        for event in Events
    }

    # -- Room availabilities --
    # Dictionary mapping events to a set of rooms in which it can be held
    # R_e in paper
    RA: Dict[Event, Set[Room]] = {}

    available_types: Dict[str, Dict[str, List[str]]] = {
        const.DUMMY: [const.DUMMY],
        const.SMALL: [const.SMALL, const.MEDIUM, const.LARGE],
        const.MEDIUM: [const.MEDIUM, const.LARGE],
        const.LARGE: [const.LARGE],
        const.COMPOSITE: [const.COMPOSITE],
    }

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

    # dictionary mapping events e to the set of events in H3 hard conflict with e
    # HC_e in paper
    HC: Dict[Event, List[Event]] = {}

    # Initialise empty list for every event
    for e in Events:
        HC[e] = []

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
                    HC[event].append(curriculum_event)

    # F = the set of examination pairs with precendence constraints.
    # But actually we use the event instead
    # This occurs if they are written and oral parts of the same examination
    # and they are part of two consecutive examinations of the same course
    F: Set[Tuple[Event, Event]] = set()

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
                secondary_course = courseManager.get_course_by_name(
                    secondary_course_name
                )
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
        event_course: Course = event.get_course()
        event_course_name: str = event_course.get_course_name()

        overlapping_secondary_curriculum_courses: List[Course] = []

        for curriculum in curriculaManager.get_curricula():
            secondary_course_names = curriculum.get_secondary_course_names()

            # If the course isn't secondary, we shouldn't add any of the secondary courses
            if event_course_name not in secondary_course_names:
                continue

            # This curricula containing the course in the secondary section
            # Add all the courses from the secondary part of the course into the overlapping_secondary_curriculum
            # Exclude the event_course_name
            for secondary_course_name in secondary_course_names:
                secondary_course: Course = courseManager.get_course_by_name(
                    secondary_course_name
                )
                if (
                    secondary_course not in overlapping_secondary_curriculum_courses
                    and secondary_course != event_course
                ):
                    overlapping_secondary_curriculum_courses.append(secondary_course)

        # Now convert all these courses into events using the CourseEvent dictionary
        secondary_curricula_events: List[Event] = []
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
            courseManager.get_course_by_name(name)
            for name in c.get_primary_course_names()
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
    undesired_event_periods: Dict[Event, Set[Period]] = {}
    preferred_periods: Dict[Event, Set[Period]] = {}

    for e in Events:
        if event not in preferred_periods.keys():
            preferred_periods[e] = set()

    for (
        preferred_event_period_constraint
    ) in constrManager.get_preferred_event_period_constraints():
        preferred_event_period_constraint: EventPeriodConstraint

        exam_number: int = preferred_event_period_constraint.get_exam_ordinal()

        course_name: str = preferred_event_period_constraint.get_course_name()
        course: Course = courseManager.get_course_by_name(course_name)

        period: Period = preferred_event_period_constraint.get_period()

        examination: Examination = course.get_examination_by_index(exam_number)
        exam_part: str = preferred_event_period_constraint.get_part()

        if exam_part is None:
            # exam only has one part
            event: event = examination.get_first_event()
        else:
            event: Event = examination.get_event_by_part(exam_part)

        preferred_periods[event].add(period)

    global_undesired_periods = set(
        p.get_period() for p in constrManager.get_undesired_period_constraints()
    )
    for e in Events:
        undesired_event_periods[e] = set()
        for c in constrManager.get_undesired_event_period_constraints():
            if c.get_course_name() == e.get_course_name():
                undesired_event_periods[e].add(c.get_period())

    for e in Events:
        for p in PA[e]:
            if p in global_undesired_periods or p in undesired_event_periods[e]:
                UndesiredPeriodCost[e, p] = const.P_UNDESIRED_PERIOD
            elif p not in preferred_periods[e]:
                UndesiredPeriodCost[e, p] = const.P_NOT_PREFERED_PERIOD
            else:
                UndesiredPeriodCost[e, p] = 0

    # Soft constraint undesired room violation cost for event e to be assigned to
    # period p. \alpha in the paper
    UndesiredRoomCost = {}
    undesired_event_rooms: Dict[Event, Set[Room]] = {}
    for e in Events:
        undesired_event_rooms[e] = set()

        for (
            event_room_constraint
        ) in constrManager.get_undesired_event_room_constraints():
            room_name: str = event_room_constraint.get_room_name()
            room: Room = Rooms.get_room_by_name(room_name)

            if event_room_constraint.get_course_name() == e.get_course_name():
                undesired_event_rooms[e].add(room)

    for e in Events:
        for r in RA[e]:
            if r in undesired_event_rooms[e]:
                UndesiredRoomCost[e, r] = const.P_UNDESIRED_ROOM
            else:
                UndesiredRoomCost[e, r] = 0

    # Dictionary mapping teachers to the set of events corresponding to courses
    # taught by that teacher.
    teacherEvents = {}
    for course in courseManager.get_courses():
        course_teacher = course.get_teacher()
        if course_teacher in teacherEvents:
            teacherEvents[course_teacher] |= {
                ev for e in course.get_examinations() for ev in e.get_events()
            }
        else:
            teacherEvents[course_teacher] = {
                ev for e in course.get_examinations() for ev in e.get_events()
            }

    # Dictionary mapping curricula to events corresponding to their primary
    # courses.
    primary_events = {
        curr: {
            e
            for name in curr.get_primary_course_names()
            for exam in courseManager.get_course_by_name(name).get_examinations()
            for e in exam.get_events()
        }
        for curr in curriculaManager.get_curricula()
    }

    # Set of all unorded pairs of events (stored as a frozenset) which are in
    # S1 soft conflict
    P1 = set()
    # Soft conflict cost for each pair
    SOFT_CONFLICT = {}
    # Add primary-secondary conflicts first
    for c in curriculaManager.get_curricula():
        for name1 in c.get_primary_course_names():
            for name2 in c.get_secondary_course_names():
                new_events = {
                    frozenset((ev1, ev2))
                    for ex1 in courseManager.get_course_by_name(
                        name1
                    ).get_examinations()
                    for ex2 in courseManager.get_course_by_name(
                        name2
                    ).get_examinations()
                    for ev1 in ex1.get_events()
                    for ev2 in ex2.get_events()
                }
                for e in new_events:
                    P1.add(e)
                    SOFT_CONFLICT[e] = const.SC_PRIMARY_SECONDARY
    # Add secondary-secondary conflicts -- BE CAREFUL NOT TO OVERWRITE PREIMARY-PRIMARY COSTS
    for c in curriculaManager.get_curricula():
        for name1 in c.get_secondary_course_names():
            for name2 in c.get_secondary_course_names():
                new_events = {
                    frozenset((ev1, ev2))
                    for ex1 in courseManager.get_course_by_name(
                        name1
                    ).get_examinations()
                    for ex2 in courseManager.get_course_by_name(
                        name2
                    ).get_examinations()
                    for ev1 in ex1.get_events()
                    for ev2 in ex2.get_events()
                }
                for e in new_events:
                    if e not in P1:
                        P1.add(e)
                        SOFT_CONFLICT[e] = const.SC_SECONDARY_SECONDARY

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
    Y = {(e, p): BMP.addVar(vtype=GRB.BINARY) for e in Events for p in PA[e]}

    # The ordinal (order) value of the period assigned to event e
    H = {e: BMP.addVar(vtype=GRB.INTEGER) for e in Events}

    # The penalty for an S1 soft conflict between a pair of events.
    # Can definitely be relaxed to continuous
    S1 = {s: BMP.addVar() for s in P1}

    # estimate of the number of events allocated to undesired rooms in each period
    # Can definitely be relaxed to continuous
    S2 = {p: BMP.addVar() for p in Periods}

    # S3 things
    PMinE = {(e1, e2): BMP.addVar(vtype=GRB.CONTINUOUS) for (e1, e2) in DPSameCourse}
    PMinWO = {(e1, e2): BMP.addVar(vtype=GRB.CONTINUOUS) for (e1, e2) in DPWrittenOral}
    PMaxWO = {(e1, e2): BMP.addVar(vtype=GRB.CONTINUOUS) for (e1, e2) in DPWrittenOral}
    PMinPP = {
        (e1, e2): BMP.addVar(vtype=GRB.CONTINUOUS) for (e1, e2) in DPPrimaryPrimary
    }
    PMinPS = {
        (e1, e2): BMP.addVar(vtype=GRB.CONTINUOUS) for (e1, e2) in DPPrimarySecondary
    }

    # Variables for S3 soft constraints
    # Abs distances between assignment of e1 and e2
    # NOOOOOOO why does this exist; we should ALWAYS write D_actual_abs_1 +
    #   D_actual_abs_2 instead TODO TODO
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

    print("Variables Defined:", time.time() - previous_time, const.SECONDS)
    previous_time = time.time()
    # ------ Constraints ------

    # Limits every event to be assigned exactly 1 period
    # OnePeriodPerEvent = {
    #     e: BMP.addConstr(quicksum(Y[e, p] for p in Periods) == 1) for e in Events
    # }

    # Hard upper limit on the number of events assigned to a period
    # Total number of rooms around campus
    num_rooms: int = len(Rooms.get_single_rooms())

    # Rooms available per period
    # Dict mapping (Period, room_type, room_size) to number of rooms available
    rooms_available: Dict[Tuple[Period, str, int], int] = {}

    # Rooms available by size per period
    forbidden_rooms_by_period_and_type: Dict[
        Tuple[Period, Union[const.SMALL, const.MEDIUM, const.LARGE]], List[Room]
    ] = {}
    undesired_rooms_by_period_and_type: Dict[
        Tuple[Period, Union[const.SMALL, const.MEDIUM, const.LARGE]], List[Room]
    ] = {}

    for p in Periods:
        for room_type in const.ROOM_TYPES:
            for room_size in range(
                1, Rooms.get_max_members_by_room_type(room_type) + 1
            ):
                # Set to the number of rooms of this type and size
                rooms_available[
                    p, room_type, room_size
                ]: int = Rooms.get_num_compatible_rooms(room_type, room_size)

                # Subtract any forbidden rooms. Only considering forbidden room period constraints here.
                for (
                    forbidden_room_period_constraint
                ) in constrManager.get_forbidden_room_period_constraints():
                    frpc_period = forbidden_room_period_constraint.get_period()
                    frpc_room: Room = Rooms.get_room_by_name(
                        forbidden_room_period_constraint.get_room_name()
                    )
                    frpc_room_type: str = frpc_room.get_type()
                    frpc_room_size: int = frpc_room.get_num_members()

                    if (
                        frpc_period == p
                        and frpc_room_type == room_type
                        and frpc_room_size
                        in Rooms.get_compatible_room_types(room_type, room_size)
                    ):
                        rooms_available[p, room_type, room_size] -= 1

                # A pre-cut for the BSP
                BMP.addConstr(
                    quicksum(
                        Y[e, p]
                        for e in Events
                        if p in PA[e]
                        if e.get_room_type() != const.DUMMY
                        and e.get_num_rooms() == room_size
                        and e.get_room_type() == room_type
                    )
                    <= Rooms.get_num_compatible_rooms(room_type, room_size)
                    #     - quicksum(
                    #         Y[e, p]
                    #         * e.get_num_rooms()
                    #         * Rooms.get_independence_number(
                    #             e.get_room_type(), e.get_num_rooms()
                    #         )
                    #         for e in Events
                    #         if p in PA[e]
                    #         and e.get_num_rooms() > room_size
                    #         and e.get_room_type() == room_type
                    #     )
                    #     - quicksum(
                    #         Y[e, p]
                    #         for e in Events
                    #         if p in PA[e]
                    #         and room_size == 1
                    #         and e.get_num_rooms() == room_size
                    #         and e.get_room_type()
                    #         in Rooms.get_compatible_room_types(room_type, room_size)[1:]
                    #         # Where the room type is effectively "larger" hence [1:].
                    #     )
                )
        # Number of rooms available by size per period
        # This will be handy for callback

        for room_type in const.ROOM_TYPES:
            # Initialise empty list for every period and room type
            forbidden_rooms_by_period_and_type[(p, room_type)] = []
            undesired_rooms_by_period_and_type[(p, room_type)] = []

            for (
                forbidden_room_period_constraint
            ) in constrManager.get_forbidden_room_period_constraints():
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

                # print("Adding forbidden room in period", p, room_type, room)

                forbidden_rooms_by_period_and_type[(p, room_type)].append(room)

                # Check if room is part of any composite rooms
                # If so, add the composite room to the forbidden list as well
                for composite_room in CompositeRooms:
                    composite_room_members = composite_room.get_members()
                    if room_name in composite_room_members:
                        forbidden_rooms_by_period_and_type[(p, room_type)].append(
                            composite_room
                        )

            for (
                undesired_room_period_constraint
            ) in constrManager.get_undesired_room_period_constraints():
                undesired_room_period_constraint: RoomPeriodConstraint

                room_period_constraint_period: Period = (
                    undesired_room_period_constraint.get_period()
                )
                level: str = undesired_room_period_constraint.get_level()
                room_name: str = undesired_room_period_constraint.get_room_name()
                room: Room = Rooms.get_room_by_name(room_name)

                if level != const.UNDESIRED:
                    continue

                if room_period_constraint_period != p:
                    continue

                if room.get_type() != room_type:
                    continue

                # print("Adding undesired room in period", p, room_type, room_name)

                undesired_rooms_by_period_and_type[(p, room_type)].append(room_name)

    # Dictionary mapping periods to the set of rooms available (i.e. not forbidden)
    # in that period. Used in BSP
    RoomsAvailable = {
        p: {r for r in Rooms if not constrManager.is_forbidden(r.get_room(), p)}
        for p in Periods
    }

    # Number of available rooms by period, type of room, and number of joining members
    # Excludes forbidden room_period constraints
    # Number of joining members = 1 => single room
    # Number of joining members > 1 => composite room
    available_rooms_by_period_type_and_size: Dict[
        Tuple[Period, str, int], List[Room]
    ] = {}

    # Begin by assigning all periods to have the same number of available rooms
    for period in Periods:
        for room_type in const.ROOM_TYPES:
            if Rooms.get_max_members_by_room_type(room_type) == 0:
                continue

            for num_members in range(
                1, Rooms.get_max_members_by_room_type(room_type) + 1
            ):
                available_rooms_by_period_type_and_size[
                    (period, room_type, num_members)
                ] = [
                    room
                    for room in Rooms.get_rooms_by_size_and_num_rooms(
                        room_type, num_members
                    )
                    if room
                    not in forbidden_rooms_by_period_and_type[(period, room_type)]
                ]

    # Each event is scheduled to exactly one time period
    ScheduledOnce = {
        e: BMP.addConstr(quicksum(Y[e, p] for p in PA[e]) == 1) for e in Events
    }

    # Constraint 4: Some events must precede other events
    Precendences = {(e1, e2): BMP.addConstr(H[e1] - H[e2] <= -1) for (e1, e2) in F}

    # Constraint 5: H3 hard conflicts
    HardConflictsPrimary = {
        (c, p): BMP.addConstr(
            quicksum(Y[e, p] for e in primary_events[c] if p in PA[e]) <= 1
        )
        for c in curriculaManager.get_curricula()
        for p in Periods
    }
    HardConflictsTeacher = {
        (t, p): BMP.addConstr(
            quicksum(Y[e, p] for e in teacherEvents[t] if p in PA[e]) <= 1
        )
        for t in teacherEvents  # loops over keys
        for p in Periods
    }

    # Constraint 7: Set values of H_e
    setH = {
        e: BMP.addConstr(
            quicksum(p.get_ordinal_value() * Y[e, p] for p in PA[e]) == H[e]
        )
        for e in Events
    }

    # Sharp lower bound on the of S1 estimation variables.
    # Note that, by default, there is already a lower bound of 0
    SoftConflicts = {
        (s, p): BMP.addConstr(
            S1[s] >= SOFT_CONFLICT[s] * (-1 + quicksum(Y[e, p] for e in s))
        )
        for s in P1
        for p in utils.intersection(PA[e] for e in s)
    }

    # Constraint 10 (S3): DirectedDistances
    Constraint10 = {
        (e1, e2): BMP.addConstr(D_abs[e1, e2] == H[e2] - H[e1])
        for (e1, e2) in DPDirected
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

        Constraint20[(e1, e2)] = BMP.addConstr(
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

        Constraint21[(written_event, oral_event)] = BMP.addConstr(
            PMinWO[written_event, oral_event] + D_abs[written_event, oral_event]
            >= min_distance
        )
        Constraint22[(written_event, oral_event)] = BMP.addConstr(
            D_abs[written_event, oral_event] - PMaxWO[written_event, oral_event]
            <= max_distance
        )

    Constraint23 = {}
    for e1, e2 in DPPrimaryPrimary:
        e1_course: Course = e1.get_course()
        e2_course: Course = e2.get_course()

        Constraint23[(e1, e2)] = BMP.addConstr(
            PMinPP[e1, e2] + D_abs[e1, e2] >= primary_primary_distance
        )

    Constraint24 = {}
    for e1, e2 in DPPrimarySecondary:
        e1_course: Course = e1.get_course()
        e2_course: Course = e2.get_course()

        Constraint24[(e1, e2)] = BMP.addConstr(
            PMinPS[e1, e2] + D_abs[e1, e2] >= primary_primary_distance
        )

    print("Constraints defined", time.time())

    # ------ Objective Function ------

    BMP.setObjective(
        # Cost S1
        quicksum(S1[s] for s in P1)
        # Cost S2
        + const.P_UNDESIRED_PERIOD
        * (
            quicksum(
                Y[e, p]
                for e in Events
                for p in PA[e]
                if p in constrManager.get_period_constraints()
                if p.period in PA[e]
            )
            + quicksum(Y[e, p] for e in Events for p in undesired_event_periods[e])
        )
        + const.P_NOT_PREFERED_PERIOD
        * quicksum(
            1 - Y[e, p] for e in Events for p in PA[e] if p in preferred_periods[e]
        )
        + const.P_UNDESIRED_ROOM * quicksum(S2[p] for p in Periods)
        # Cost S3
        + const.DD_SAME_COURSE * quicksum(PMinE[e1, e2] for (e1, e2) in DPSameCourse)
        + const.DD_SAME_EXAMINATION
        * quicksum(PMinWO[e1, e2] + PMaxWO[e1, e2] for (e1, e2) in DPWrittenOral)
        + const.UD_PRIMARY_PRIMARY
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

    # Keeps track of set of events we've seen. If we've seen this set before in period p and the BSP was
    # infeasible then add a no good cut.
    seem_event_sets: Dict[Period, Set[frozenset[Event]]] = {p: set() for p in Periods}

    X_global: Dict[Tuple[Event, Period], Room] = {}

    def Callback(model, where):
        if where != GRB.Callback.MIPSOL:
            return

        print("Callback")
        YV = model.cbGetSolution(Y)

        numCuts = 0

        for p in Periods:
            # Sets

            # Set of events that are assigned to period p (from the master problem)
            EventsP = {e for e in Events if p in PA[e] and YV[e, p] > 0.9}

            # Set of events assigned to period p requiring room with type room_type and # members num_rooms
            events_p_by_type_and_size: Dict[Tuple[str, int], List[Event]] = {}
            for room_type in const.ROOM_TYPES:
                for room_size in range(
                    1, Rooms.get_max_members_by_room_type(room_type) + 1
                ):
                    events_p_by_type_and_size[(room_type, room_size)] = [
                        e
                        for e in EventsP
                        if e.get_room_type() == room_type
                        and e.get_num_rooms() == room_size
                    ]

            OverlappingP = {
                rc: Rooms.get_overlapping_rooms(rc) & RoomsAvailable[p]
                for rc in CompositeRooms
            }

            # Define Sub Problem
            BSP = Model("BSP for Period " + str(p))

            # Set output flag off/on
            BSP.setParam("OutputFlag", 0)

            # Variables in Subproblem

            # X = 1 if event e is assigned to period p and room r, 0 else
            X = {(e, r): BSP.addVar(vtype=GRB.BINARY) for e in EventsP for r in Rooms}

            # Subproblem objective function

            BSP.setObjective(
                quicksum(
                    X[e, r]
                    for e in EventsP
                    for r in undesired_event_rooms[e]
                    if r in RA[e]
                ),
                GRB.MINIMIZE,
            )

            # Subproblem Constraints

            # Each event assigned to an available period and exactly 1 room.
            AssignedRooms = {
                e: BSP.addConstr(
                    quicksum(X[e, r] for r in RA[e] & RoomsAvailable[p]) == 1
                )
                for e in EventsP
            }

            # At most one event can use a room at once.
            RoomClashes = {
                r: BSP.addConstr(quicksum(X[e, r] for e in EventsP if r in RA[e]) <= 1)
                for r in RoomsAvailable[p]
                if r is not dummy_room
            }

            # Composite room overlap
            CompositeOverlap = {
                rc: BSP.addConstr(
                    len(OverlappingP[rc])
                    * quicksum(X[e, rc] for e in EventsP if rc in RA[e])
                    + quicksum(
                        X[e, r0]
                        for r0 in OverlappingP[rc]
                        for e in EventsP
                        if r0 in RA[e]
                    )
                    <= len(OverlappingP[rc])
                )
                for rc in CompositeRooms & RoomsAvailable[p]
            }

            BSP.optimize()

            # Check if BSP is infeasible. If it is, I need to add a feasability cut to prevent as many events
            # being allocated to this period

            if BSP.status == GRB.INFEASIBLE:
                print("##############   Infeasible subproblem")
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
                        if YV[e, p] > 0.9 and e.get_room_type() == room_type:
                            # Add the number of rooms required by the event.
                            room_allocations[room_type] += e.get_num_rooms()

                # Just remember that a room request of small can use larger rooms
                # but this doesn't apply to composite rooms

                # Add a no good cut to say this exact combination isn't feasible

                # Uncomment to add no good cut
                # if frozenset(EventsP) in seem_event_sets[p]:
                #     print("Adding no Good cut", p)
                #     model.cbLazy(quicksum((1 - Y[e, p]) for e in EventsP) >= 1)

                # Idea of other constraint I had
                # Feasibility cut is different for each room type.
                print("Adding feasibility cut for period", p)
                for room_type in const.ROOM_TYPES:
                    # SMALL, MEDIUM and LARGE, excluding composite.
                    if Rooms.get_max_members_by_room_type(room_type) == 0:
                        continue

                    for room_size in range(
                        1, Rooms.get_max_members_by_room_type(room_type) + 1
                    ):
                        # Limit the number of events allocated to period p of type room_type
                        # with num_members members

                        # For now just constrain number of events to number of rooms available in the period
                        # regardless of type
                        model.cbLazy(
                            quicksum(
                                Y[e, p]
                                for e in EventsP
                                if e.get_room_type() != const.DUMMY
                                and e.get_num_rooms() == room_size
                                and e.get_room_type() == room_type
                            )
                            <= Rooms.get_num_compatible_rooms(room_type, room_size)
                            - quicksum(
                                Y[e, p]
                                * e.get_num_rooms()
                                * Rooms.get_independence_number(
                                    e.get_room_type(), e.get_num_rooms()
                                )
                                for e in EventsP
                                if e.get_num_rooms() > room_size
                                and e.get_room_type() == room_type
                            )
                            - quicksum(
                                Y[e, p]
                                for e in EventsP
                                if room_size == 1
                                and e.get_num_rooms() == room_size
                                and e.get_room_type()
                                in Rooms.get_compatible_room_types(
                                    room_type, room_size
                                )[1:]
                                # Where the room type is effectively "larger" hence [1:].
                            )
                        )

                # Now go solve the master problem again
            else:
                # BSP is feasible.
                # Set X_global so we can access this later during printing

                for e in EventsP:
                    for r in RA[e]:
                        if X[e, r].x > 0.9:
                            X_global[e, p] = r

                # Update the objective function of the master problem
                # print("Adding optimality cut for period", p, S2V[p], BSP.objVal)
                model.cbLazy(
                    S2[p]
                    >= BSP.objVal
                    * (
                        1
                        - quicksum(
                            (1 - Y[e, p])
                            for e in EventsP
                            if len(undesired_event_rooms[e]) > 0
                        )
                    )
                )

            # Add to seem_event_sets

            seem_event_sets[p].add(frozenset(EventsP))

            numCuts += 1

    BMP.setParam("OutputFlag", 1)
    BMP.setParam("MIPGap", 0)
    BMP.setParam("LazyConstraints", 1)
    BMP.optimize(Callback)

    # ------ Print output ------

    print("----")
    print("\n\nFinal Objective Value:", BMP.ObjVal, "\n\n")

    for d in Days:
        print("------" * 10 + "\nDay ", d)
        for p in Periods:
            if p.get_day() == d:
                # print(f"{' '*4}Period ", p)
                for e in Events:
                    # Ensure we check if p in available periods for event e before accessing Y[e, p]
                    if p in PA[e] and Y[e, p].x > 0.9:
                        print(f"{' '*4} Period {p}: exam {e}")

                        # If we know event e is assigned period p, loop over the rooms to find out which one
                        # for r in RA[e]:
                        #     if X[e, r].x > 0.9:
                        #         print(f"{' '*4} Period {p}: exam {e} in in room {r}")

    print("------" * 10)


def main():
    problem_path = os.path.join(".", "Project", "data")
    for filename in os.listdir(problem_path):
        if os.path.isfile(os.path.join(problem_path, filename)):
            if filename != "D3-1-16.json":
                continue

            solve(filename)

            print("\n\n")

    print("Done")


if __name__ == "__main__":
    main()
