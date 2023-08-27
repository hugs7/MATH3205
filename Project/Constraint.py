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


class ConstraintManager:
    def __init__(self):
        self.constraints = []

    def add_constraint(self, constraint_data):
        new_constraint = Constraint(constraint_data)
        self.constraints.append(new_constraint)

    def __str__(self):
        return "\n".join([str(constraint) for constraint in self.constraints])
