import json
import os
from typing import List
import Constants as const
from Constraint import ConstraintManager
from Course import Course, CourseManager
from Curriculum import CurriculaManager
from Event import Event
from Period import Period
from Room import RoomManager


# ------ Import data ------

instance_name = "D1-3-16.json"
data_file = os.path.join(".", "Project", "data", instance_name)
with open(data_file, "r") as json_file:
    json_data = json_file.read()

solution_file = os.path.join(
    ".", "Project", "Solutions", "BestSolutions", f"sol_{instance_name}"
)

with open(solution_file, "r") as json_sol_file:
    json_sol_file = json_sol_file.read()

# ------ Parse data with JSON ------

parsed_data = json.loads(json_data)
solution_data = json.loads(json_sol_file)

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

room_constraints = constrManager.get_room_period_constraints()
event_room_constraints = constrManager.get_event_room_constraints()

# Event period Constraints
event_constraints = constrManager.get_event_period_constraints()
period_constraints = constrManager.get_period_constraints()

# Forbidden period constraints (any event any room)
# Convert periods into day and timeslot tuples
forbidden_period_constraints: List[Period] = [
    period_constraint.get_period().get_ordinal_value()
    for period_constraint in constrManager.get_forbidden_period_constraints()
]
course_min_distance = {}
for i in courseManager.courses:
    course_min_distance[i.course_name] = i.get_min_distance_between_exams()

courses_in_curr = {}
primary = {}
secondary = {}
for c in curriculaManager.curricula:
    courses_in_curr[c.name] = [c1 for c1 in c.get_course_names()]
    primary[c.name] = [c1 for c1 in c.primary_course_names]
    secondary[c.name] = [c1 for c1 in c.secondary_course_names]

assignments = solution_data["Assignments"]
events: dict[Course, List[Event]] = {}
broken_forbidden_period = 0
broken_event_period = 0
undes_event_period = 0
broken_undesired_period = 0
broken_undesired_room = 0
broken_forbidden_room = 0
for a in assignments:
    course_name = a["Course"]
    events[course_name] = a["Events"]

    min_distance = course_min_distance[course_name]
    if min_distance == None:
        min_distance = 0
    if len(events[course_name]) > 1:
        breakpoint()
        if (
            abs(
                events[course_name][0].get("Period")
                - events[course_name][1].get("Period")
            )
            < min_distance
        ):
            print(
                "Broken min distance constraint: ",
                course_name,
                events[course_name][0].get("Period"),
                events[course_name][1].get("Period"),
            )

    for e in events[course_name]:
        exam = e["Exam"]
        part = e["Part"]
        period = e["Period"]
        room = e.get("Room")

        for p in forbidden_period_constraints:
            if p == period:
                print("Broken Period Constraint: ", course_name, exam, part, period)
                broken_forbidden_period += 1

        for p in period_constraints:
            if p.get_period().get_ordinal_value() not in forbidden_period_constraints:
                if p.get_period().get_ordinal_value() == period:
                    print(
                        "Broken Undesired Period Constraint: ",
                        course_name,
                        exam,
                        part,
                        period,
                    )
                    broken_undesired_period += 1

        for e in event_constraints:
            if (
                e.course_name == course_name
                and e.exam_ordinal == exam
                and not e.get_period().get_ordinal_value() == period
            ):
                print(
                    "Broken Event Period Constraint: ", course_name, exam, part, period
                )
                if e.level == "Preferred":
                    broken_event_period += 1
                elif e.level == "Undesired":
                    broken_undesired_period += 1

        for r in room_constraints:
            if (
                not r.get_room() == room
                and r.get_period().get_ordinal_value() == period
            ):
                if r.get_level() == const.FORBIDDEN:
                    print(
                        "Broken Forbidden Room Constraint: ",
                        course_name,
                        exam,
                        part,
                        period,
                        room,
                    )
                    broken_forbidden_room += 1
                elif r.get_level() == const.UNDESIRED:
                    print(
                        "Broken Undesired Room Constraint: ",
                        course_name,
                        exam,
                        part,
                        period,
                        room,
                    )
                    broken_undesired_room += 1

        for r in event_room_constraints:
            if (
                r.course_name == course_name
                and r.part == part
                and r.get_part() == part
                and r.room == room
                and r.exam_ordinal == exam
            ):
                if r.get_level() == const.FORBIDDEN:
                    print(
                        "Broken Forbidden Event Room Constraint: ",
                        course_name,
                        exam,
                        part,
                        period,
                        room,
                    )
                elif r.get_level() == const.UNDESIRED:
                    print(
                        "Broken Undesired Event Room Constraint: ",
                        course_name,
                        exam,
                        part,
                        period,
                        room,
                    )

curruculas = curriculaManager.curricula
count = 0
primary_secondary_distance = 1
same_period_pp = 0
same_period_ps = 0
same_period_ss = 0

for c in curruculas:
    primary_primary = {}
    secondary = {}
    for a in assignments:
        if a["Course"] in c.get_primary_course_names():
            for e in a["Events"]:
                primary_primary[(a["Course"], e["Exam"], e["Part"])] = e["Period"]
        if a["Course"] in c.get_secondary_course_names():
            for e in a["Events"]:
                secondary[(a["Course"], e["Exam"], e["Part"])] = e["Period"]
    index1 = -1
    for p1 in primary_primary.values():
        index1 += 1
        index2 = -1
        for p2 in primary_primary.values():
            index2 += 1
            if abs(p1 - p2) < primary_primary_distance - 1:
                if (
                    index1 != index2
                    and list(primary_primary.keys())[index1][0]
                    != list(primary_primary.keys())[index2][0]
                ):
                    if (
                        len(events[str(list(primary_primary.keys())[index1][0])]) > 1
                        or len(events[str(list(primary_primary.keys())[index2][0])]) > 1
                    ):
                        if (
                            (
                                list(primary_primary.keys())[index1][2] == "Written"
                                and list(primary_primary.keys())[index2][2] == "Written"
                            )
                            or list(primary_primary.keys())[index2][2] == "Written"
                            or list(primary_primary.keys())[index1][2] == "Written"
                        ):
                            count += 1
                            print(p1, p2, p1 - p2)
                            print(
                                list(primary_primary.keys())[index1],
                                list(primary_primary.keys())[index2],
                            )
                    else:
                        count += 1
                        print(p1, p2, p1 - p2)
                        print(
                            list(primary_primary.keys())[index1],
                            list(primary_primary.keys())[index2],
                        )

            if p1 == p2 and index1 != index2:
                print(
                    "Same period:",
                    p2,
                    list(primary_primary.keys())[index1],
                    list(primary_primary.keys())[index2],
                )
                same_period_pp = +1
    index1 = -1
    count_ps_distance = 0
    for p1 in primary_primary.values():
        index1 += 1
        index2 = -1
        for p2 in secondary.values():
            index2 += 1
            if (
                abs(p1 - p2) < primary_secondary_distance
                and p1 - p2 != 0
                and list(primary_primary.keys())[index1][0]
                != list(secondary.keys())[index2][0]
            ):
                if (
                    len(events[str(list(primary_primary.keys())[index1][0])]) > 1
                    or len(events[str(list(secondary.keys())[index2][0])]) > 1
                ):
                    if (
                        (
                            list(primary_primary.keys())[index1][2] == "Written"
                            and list(secondary.keys())[index2][2] == "Written"
                        )
                        or list(secondary.keys())[index2][2] == "Written"
                        or list(secondary.keys())[index1][2] == "Written"
                    ):
                        count_ps_distance += 1
                        print(p1, p2, p1 - p2)
                        print(
                            list(primary_primary.keys())[index1],
                            list(secondary.keys())[index2],
                        )
                else:
                    count_ps_distance += 1
                    print(p1, p2, p1 - p2)
                    print(
                        list(primary_primary.keys())[index1],
                        list(secondary.keys())[index2],
                    )
            if p1 == p2 and index1 != index2:
                print(
                    "Same period:",
                    p2,
                    list(primary_primary.keys())[index1],
                    list(secondary.keys())[index2],
                )
                same_period_ps += 1
    index1 = -1
    for p1 in secondary.values():
        index1 += 1
        index2 = -1
        for p2 in secondary.values():
            index2 += 1
            if p1 == p2 and index1 != index2:
                print(
                    "secondary secondary same period:",
                    p1,
                    list(secondary.keys())[index1],
                    list(secondary.keys())[index2],
                )
                same_period_ss += 1
min_distance_not_attained_same_exam = 0
min_distance_not_attained_diff_exam = 0
for a in assignments:
    course_name = a["Course"]
    for c in parsed_data["Courses"]:
        if c.get("MinimumDistanceBetweenExams") and c["Course"] == course_name:
            for e in events[course_name]:
                for e2 in events[course_name]:
                    if e["Part"] != e2["Part"] and e["Exam"] == e2["Exam"]:
                        max_distance = c["WrittenOralSpecs"]["MaxDistance"]
                        min_distance = c["WrittenOralSpecs"]["MinDistance"]
                        if (
                            abs(e["Period"] - e2["Period"]) < min_distance
                            or abs(e["Period"] - e2["Period"]) > max_distance
                        ):
                            min_distance_not_attained_same_exam += 1
                    elif (
                        e["Exam"] != e2["Exam"]
                        and e["Part"] == "Written"
                        and e2["Part"] == "Written"
                    ):
                        if abs(e["Period"] - e2["Period"]) < c.get(
                            "MinimumDistanceBetweenExams"
                        ):
                            min_distance_not_attained_diff_exam += 1
                    elif (
                        e["Exam"] != e2["Exam"]
                        and e["Part"] == "Written"
                        and e2["Part"] == "Oral"
                    ):
                        if abs(e["Period"] - e2["Period"]) < c.get(
                            "MinimumDistanceBetweenExams"
                        ):
                            min_distance_not_attained_diff_exam += 1
                    elif (
                        e["Exam"] != e2["Exam"]
                        and e["Part"] == "Oral"
                        and e2["Part"] == "Oral"
                    ):
                        if abs(e["Period"] - e2["Period"]) < c.get(
                            "MinimumDistanceBetweenExams"
                        ):
                            min_distance_not_attained_diff_exam += 1


print(
    "Objective is: ",
    broken_undesired_period * const.P_UNDESIRED_PERIOD
    + broken_event_period * 2
    + broken_undesired_room * const.P_UNDESIRED_ROOM
    + count * 2
    + count_ps_distance * 2
    + same_period_ps * 5
    + same_period_ss * 1
    + min_distance_not_attained_same_exam * 15
    + min_distance_not_attained_diff_exam * 12,
)
