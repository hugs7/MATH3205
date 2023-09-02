"""
Class for handing constraints (hard and soft) in the problem
"""


class Constraint:
    def __init__(self, constraint_data):
        self.level = constraint_data.get("Level")
        self.period = constraint_data.get("Period")
        self.room = constraint_data.get("Room")
        self.type = constraint_data.get("Type")
        self.course = constraint_data.get("Course")
        self.exam = constraint_data.get("Exam")
        self.part = constraint_data.get("Part")

    def __repr__(self):
        if self.type == "RoomPeriodConstraint":
            return f"Forbidden Room {self.room} at Period {self.period}"
        elif self.type == "EventPeriodConstraint":
            if self.part:
                return f"{self.level} {self.course} Exam {self.exam} - {self.part} at Period {self.period}"
            else:
                return f"{self.level} {self.course} Exam {self.exam} at Period {self.period}"
        elif self.type == "PeriodConstraint":
            return f"{self.level} at Period {self.period}"

    def is_room_constraint(self) -> bool:
        return self.type == "RoomPeriodConstraint"

    def is_event_period_constraint(self) -> bool:
        return self.type == "EventPeriodConstraint"

    def is_period_constraint(self) -> bool:
        return self.type == "PeriodConstraint"

    def is_forbidden(self) -> bool:
        return self.level == "Forbidden"

    def is_undesired(self) -> bool:
        return self.level == "Undesired"

    def get_level(self):
        return self.level


class ConstraintManager:
    def __init__(self):
        self.constraints = []

    def add_constraint(self, constraint_data):
        new_constraint = Constraint(constraint_data)
        self.constraints.append(new_constraint)

    def __str__(self):
        return "\n".join([str(constraint) for constraint in self.constraints])

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.constraints):
            constraint = self.constraints[self._index]
            self._index += 1
            return constraint
        else:
            raise StopIteration

    def get_course_list(self) -> list:
        course_list = []
        for constr in self.constraints:
            if constr.course not in course_list and constr.course != None:
                course_list.append(constr.course)
        return course_list

    def get_room_constraints(self) -> dict[int, dict[str, str]]:
        room_constraints = {}
        for constr in self.constraints:
            if constr.is_room_constraint():
                room_constraints[constr.period] = {}
                room_constraints[constr.period].update({constr.room: constr.level})
        return room_constraints

    def get_event_constraints(self) -> dict[str, (str, str, int, int)]:
        event_constraints = {}
        for course in self.get_course_list():
            temp = []
            for constr in self.constraints:
                if constr.is_event_period_constraint() and constr.course == course:
                    temp.append((constr.level, constr.part, constr.exam, constr.period))
            event_constraints[course] = temp
        return event_constraints

    def get_period_constraints(self) -> dict[int, str]:
        period_constraints = {}
        for constr in self.constraints:
            constr: Constraint
            if constr.is_period_constraint():
                period_constraints[constr.period] = constr.level
        return period_constraints

    def get_forbidden_period_constraints(self) -> int:
        period_constraints = []
        for constr in self.constraints:
            constr: Constraint
            if constr.is_period_constraint() and constr.is_forbidden():
                period_constraints.append(constr.period)
        return period_constraints

    def get_undesired_period_constraints(self) -> int:
        period_constraints = []
        for constr in self.constraints:
            constr: Constraint
            if constr.is_period_constraint() and constr.is_undesired():
                period_constraints.append(constr.period)
        return period_constraints
