"""
Class for handing constraints (hard and soft) in the problem
"""

from abc import ABC
from typing import List, Optional

from Period import Period


ROOM_PERIOD_CONSTRAINT = "RoomPeriodConstraint"
EVENT_PERIOD_CONSTRAINT = "EventPeriodConstraint"
EVENT_ROOM_CONSTRAINT = "EventRoomConstraint"
PERIOD_CONSTRAINT = "PeriodConstraint"

FORBIDDEN = "Forbidden"
UNDESIRED = "Undesired"


class Constraint(ABC):
    def __init__(self, constraint_data, slots_per_day: int):
        self.level = constraint_data.get("Level")

        self.constr_type = constraint_data.get("Type")

    # Getter method for 'Level' attribute
    def get_level(self) -> str:
        """
        Get the 'Level' attribute.
        Returns:
            Optional[str]: The 'Level' value or None if it doesn't exist.
        """
        return self.level

    # Getter method for 'Type' attribute
    def get_constr_type(self) -> str:
        """
        Get the 'Type' attribute.
        Returns:
            str: The 'Type' value or None if it doesn't exist.
        """
        return self.constr_type

    def get_level(self):
        return self.level

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


class RoomPeriodConstraint(Constraint):
    def __init__(self, constraint_data, slots_per_day: int):
        super().__init__(constraint_data, slots_per_day)

        self.room = constraint_data.get("Room")
        self.period: Period = Period.from_period_number(
            constraint_data.get("Period"), slots_per_day
        )
        self.part = constraint_data.get("Part")

    def __repr__(self):
        return f"Forbidden Room {self.room} at Period {self.period}"

    # Getter method for 'Room' attribute
    def get_room(self) -> str:
        """
        Get the 'Room' attribute.
        Returns:
            Optional[str]: The 'Room' value or None if it doesn't exist.
        """
        return self.room

    # Getter method for 'Period' attribute
    def get_period(self) -> Period:
        """
        Get the 'Period' attribute.
        Returns:
            Optional[str]: The 'Period' value or None if it doesn't exist.
        """
        return self.period

    # Getter method for 'Part' attribute
    def get_part(self) -> Optional[str]:
        """
        Get the 'Part' attribute.
        Returns:
            Optional[str]: The 'Part' value or None if it doesn't exist.
        """
        return self.part


class EventPeriodConstraint(Constraint):
    def __init__(self, constraint_data, slots_per_day: int):
        super().__init__(constraint_data, slots_per_day)

        self.course_name = constraint_data.get("Course")
        self.period: Period = Period.from_period_number(
            constraint_data.get("Period"), slots_per_day
        )
        self.exam_ordinal = constraint_data.get("Exam")

    # Getter method for 'Course' attribute
    def get_course_name(self) -> str:
        """
        Get the 'Course' attribute.
        Returns:
            Optional[str]: The 'Course' value or None if it doesn't exist.
        """
        return self.course_name

    def __repr__(self):
        if self.part:
            return f"{self.level} {self.course_name} Exam {self.exam_ordinal} - {self.part} at Period {self.period}"
        else:
            return f"{self.level} {self.course_name} Exam {self.exam_ordinal} at Period {self.period}"

    # Getter method for 'Period' attribute
    def get_period(self) -> Period:
        """
        Get the 'Period' attribute.
        Returns:
            Optional[str]: The 'Period' value or None if it doesn't exist.
        """
        return self.period

    # Getter method for 'Exam' attribute
    def get_exam_ordinal(self) -> int:
        """
        Get the 'Exam' attribute.
        Returns:
            Optional[str]: The 'Exam' value or None if it doesn't exist.
        """
        return self.exam_ordinal

    # Getter method for 'Part' attribute
    def get_part(self) -> Optional[str]:
        """
        Get the 'Part' attribute.
        Returns:
            Optional[str]: The 'Part' value or None if it doesn't exist.
        """
        return self.part


class EventRoomConstraint(Constraint):
    def __init__(self, constraint_data, slots_per_day: int):
        super().__init__(constraint_data, slots_per_day)

        self.room = constraint_data.get("Room")
        self.part = constraint_data.get("Part")

        # Getter method for 'Room' attribute

    def get_room(self) -> Optional[str]:
        """
        Get the 'Room' attribute.
        Returns:
            Optional[str]: The 'Room' value or None if it doesn't exist.
        """
        return self.room

    # Getter method for 'Period' attribute
    def get_period(self) -> Period:
        """
        Get the 'Period' attribute.
        Returns:
            Optional[str]: The 'Period' value or None if it doesn't exist.
        """
        return self.period

    # Getter method for 'Part' attribute
    def get_part(self) -> Optional[str]:
        """
        Get the 'Part' attribute.
        Returns:
            Optional[str]: The 'Part' value or None if it doesn't exist.
        """
        return self.part


class PeriodConstraint(Constraint):
    def __init__(self, constraint_data, slots_per_day: int):
        super().__init__(constraint_data, slots_per_day)

        self.period: Period = Period.from_period_number(
            constraint_data.get("Period"), slots_per_day
        )

    def __repr__(self):
        return f"{self.level} at Period {self.period}"

    # Getter method for 'Period' attribute
    def get_period(self) -> Period:
        """
        Get the 'Period' attribute.
        Returns:
            Optional[str]: The 'Period' value or None if it doesn't exist.
        """
        return self.period


class ConstraintManager:
    def __init__(self, slots_per_day: int):
        self.constraints: List[Constraint] = []
        self.slots_per_day = slots_per_day

    def add_constraint(self, constraint_data) -> Constraint:
        constraint_type = constraint_data.get("Type")
        if constraint_type is None:
            raise ValueError("Constraint type is missing in constraint_data")

        constraint_constructors = {
            ROOM_PERIOD_CONSTRAINT: RoomPeriodConstraint,
            EVENT_PERIOD_CONSTRAINT: EventPeriodConstraint,
            EVENT_ROOM_CONSTRAINT: EventRoomConstraint,
            PERIOD_CONSTRAINT: PeriodConstraint,
        }

        constraint_class = constraint_constructors.get(constraint_type)
        if constraint_class is None:
            raise ValueError(f"Unknown constraint type: {constraint_type}")

        new_constraint = constraint_class(constraint_data, self.slots_per_day)

        self.constraints.append(new_constraint)
        return new_constraint

    def get_constraints(self) -> List[Constraint]:
        """
        Returns list of all constraints handled by the Constraint Manager
        """

        return self.constraints

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

    # Room period constraints
    def get_room_period_constraints(self) -> List[RoomPeriodConstraint]:
        room_period_constraints = []
        for constr in self.constraints:
            if constr.is_room_constraint():
                room_period_constraints.append(constr)
        return room_period_constraints

    def get_forbidden_room_period_constraints(self) -> List[RoomPeriodConstraint]:
        forbidden_room_period_constraints = []
        for constr in self.constraints:
            if constr.is_room_constraint() and constr.is_forbidden():
                forbidden_room_period_constraints.append(constr)
        return forbidden_room_period_constraints

    def get_undesired_room_period_constraints(self) -> List[RoomPeriodConstraint]:
        undesired_room_period_constraints = []
        for constr in self.constraints:
            if constr.is_room_constraint() and constr.is_undesired():
                undesired_room_period_constraints.append(constr)
        return undesired_room_period_constraints

    # Event period Constraiats
    def get_event_period_constraints(self) -> List[EventPeriodConstraint]:
        event_period_constraints = []
        for constr in self.constraints:
            if constr.is_event_period_constraint():
                event_period_constraints.append(constr)
        return event_period_constraints

    def get_forbidden_event_period_constraints(self) -> List[EventPeriodConstraint]:
        forbidden_event_period_constraints = []
        for constr in self.constraints:
            if constr.is_event_period_constraint() and constr.is_forbidden():
                forbidden_event_period_constraints.append(constr)
        return forbidden_event_period_constraints

    def get_undesired_event_period_constraints(self) -> List[EventPeriodConstraint]:
        undesired_event_period_constraints = []
        for constr in self.constraints:
            if constr.is_event_period_constraint() and constr.is_undesired():
                undesired_event_period_constraints.append(constr)
        return undesired_event_period_constraints

    # Period Constraints
    def get_period_constraints(self) -> List[PeriodConstraint]:
        period_constraints = []
        for constr in self.constraints:
            if constr.is_period_constraint():
                period_constraints.append(constr)
        return period_constraints

    def get_forbidden_period_constraints(self) -> List[PeriodConstraint]:
        period_constraints = []
        for constr in self.constraints:
            if constr.is_period_constraint() and constr.is_forbidden():
                period_constraints.append(constr)
        return period_constraints

    def get_undesired_period_constraints(self) -> List[PeriodConstraint]:
        period_constraints = []
        for constr in self.constraints:
            if constr.is_period_constraint() and constr.is_undesired():
                period_constraints.append(constr)
        return period_constraints
