"""
Class for handing constraints (hard and soft) in the problem
"""

from typing import List, Optional


ROOM_PERIOD_CONSTRAINT = "RoomPeriodConstraint"
EVENT_PERIOD_CONSTRAINT = "EventPeriodConstraint"
PERIOD_CONSTRAINT = "PeriodConstraint"
FORBIDDEN = "Forbidden"
UNDESIRED = "Undesired"


class Constraint:
    def __init__(self, constraint_data):
        self.level = constraint_data.get("Level")
        self.period = constraint_data.get("Period")
        self.room = constraint_data.get("Room")
        self.constr_type = constraint_data.get("Type")
        self.course = constraint_data.get("Course")
        self.exam = constraint_data.get("Exam")
        self.part = constraint_data.get("Part")

    # Getter method for 'Level' attribute
    def get_level(self) -> Optional[str]:
        """
        Get the 'Level' attribute.
        Returns:
            Optional[str]: The 'Level' value or None if it doesn't exist.
        """
        return self.level

    # Getter method for 'Period' attribute
    def get_period(self) -> Optional[str]:
        """
        Get the 'Period' attribute.
        Returns:
            Optional[str]: The 'Period' value or None if it doesn't exist.
        """
        return self.period

    # Getter method for 'Room' attribute
    def get_room(self) -> Optional[str]:
        """
        Get the 'Room' attribute.
        Returns:
            Optional[str]: The 'Room' value or None if it doesn't exist.
        """
        return self.room

    # Getter method for 'Type' attribute
    def get_constr_type(self) -> Optional[str]:
        """
        Get the 'Type' attribute.
        Returns:
            Optional[str]: The 'Type' value or None if it doesn't exist.
        """
        return self.constr_type

    # Getter method for 'Course' attribute
    def get_course(self) -> Optional[str]:
        """
        Get the 'Course' attribute.
        Returns:
            Optional[str]: The 'Course' value or None if it doesn't exist.
        """
        return self.course

    # Getter method for 'Exam' attribute
    def get_exam(self) -> Optional[str]:
        """
        Get the 'Exam' attribute.
        Returns:
            Optional[str]: The 'Exam' value or None if it doesn't exist.
        """
        return self.exam

    # Getter method for 'Part' attribute
    def get_part(self) -> Optional[str]:
        """
        Get the 'Part' attribute.
        Returns:
            Optional[str]: The 'Part' value or None if it doesn't exist.
        """
        return self.part

    def __repr__(self):
        if self.constr_type == ROOM_PERIOD_CONSTRAINT:
            return f"Forbidden Room {self.room} at Period {self.period}"
        elif self.constr_type == EVENT_PERIOD_CONSTRAINT:
            if self.part:
                return f"{self.level} {self.course} Exam {self.exam} - {self.part} at Period {self.period}"
            else:
                return f"{self.level} {self.course} Exam {self.exam} at Period {self.period}"
        elif self.constr_type == PERIOD_CONSTRAINT:
            return f"{self.level} at Period {self.period}"

    def is_room_constraint(self) -> bool:
        return self.constr_type == ROOM_PERIOD_CONSTRAINT

    def is_event_period_constraint(self) -> bool:
        return self.constr_type == EVENT_PERIOD_CONSTRAINT

    def is_period_constraint(self) -> bool:
        return self.constr_type == PERIOD_CONSTRAINT

    def is_forbidden(self) -> bool:
        return self.level == FORBIDDEN

    def is_undesired(self) -> bool:
        return self.level == UNDESIRED

    def get_level(self):
        return self.level


class ConstraintManager:
    def __init__(self):
        self.constraints: List[Constraint] = []

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

    def get_event_period_constraints(self) -> dict[str, (str, str, int, int)]:
        event_constraints = {}
        for course in self.get_course_list():
            temp = []
            for constr in self.constraints:
                if constr.is_event_period_constraint() and constr.course == course:
                    temp.append((constr.level, constr.part, constr.exam, constr.period))
            event_constraints[course] = temp
        return event_constraints

    def get_forbidden_event_period_constraints(self) -> dict[str, (str, str, int, int)]:
        event_constraints = {}
        for course in self.get_course_list():
            temp = []
            for constr in self.constraints:
                if (
                    constr.is_event_period_constraint()
                    and constr.is_forbidden()
                    and constr.course == course
                ):
                    temp.append((constr.level, constr.part, constr.exam, constr.period))
            event_constraints[course] = temp
        return event_constraints

    def get_undesired_event_period_constraints(self) -> dict[str, (str, str, int, int)]:
        event_constraints = {}
        for course in self.get_course_list():
            temp = []
            for constr in self.constraints:
                if (
                    constr.is_event_period_constraint()
                    and constr.is_undesired()
                    and constr.course == course
                ):
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
