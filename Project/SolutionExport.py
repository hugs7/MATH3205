import json
import Constants as const
from typing import Dict, List
import os


# Dummy classes so that json.dumps can do all the work for us!
class _Event:
    def __init__(self, exam_index, part, period, room):
        self.Exam: int = exam_index
        self.Part: str = part
        self.Period: int = period
        if room != const.DUMMY:
            self.Room: str = room


class _Course:
    def __init__(self, course_name, events):
        self.Course = course_name
        self.Events = [e.__dict__ for e in events]


class _Solution:
    def __init__(self, assignments, cost):
        self.Assignments = [a.__dict__ for a in assignments]
        self.Cost: int = cost


class Solution:
    def __init__(self, instance_name, objective_value):
        self.instance_name: str = instance_name
        self.course_event_map: Dict[str, _Event] = {}
        self.objective_value: int = round(objective_value)

    def add_event(self, course_name, exam_index, part, period, room):
        if course_name not in self.course_event_map:
            self.course_event_map[course_name] = []
        self.course_event_map[course_name].append(
            _Event(exam_index, part, period, room)
        )

    def export(self, filename=None):
        if filename is None:
            filename = os.path.join(
                "Project", "OurSolutions", self.instance_name + "_sol.json"
            )

        assignments: List[_Course] = [
            _Course(name, self.course_event_map[name]) for name in self.course_event_map
        ]
        sol = _Solution(assignments, self.objective_value).__dict__

        with open(filename, "w") as file:
            file.write(json.dumps(sol, indent=2))
