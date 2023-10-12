"""
Class for handing constraints (hard and soft) in the problem
"""

from abc import ABC
from typing import Dict, List, Optional, Set
from Period import Period
import Constants as const


class Constraint(ABC):
    def __init__(self, constraint_data, slots_per_day: int):
        self.level = constraint_data.get(const.LEVEL)

        self.constr_type = constraint_data.get(const.TYPE)

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

    def is_room_constraint(self) -> bool:
        return self.constr_type == const.ROOM_PERIOD_CONSTRAINT

    def is_event_room_constraint(self) -> bool:
        return self.constr_type == const.EVENT_ROOM_CONSTRAINT

    def is_event_period_constraint(self) -> bool:
        return self.constr_type == const.EVENT_PERIOD_CONSTRAINT

    def is_period_constraint(self) -> bool:
        return self.constr_type == const.PERIOD_CONSTRAINT

    def is_forbidden(self) -> bool:
        return self.level == const.FORBIDDEN

    def is_undesired(self) -> bool:
        return self.level == const.UNDESIRED

    def is_preferred(self) -> bool:
        return self.level == const.PREFERRED


class RoomPeriodConstraint(Constraint):
    def __init__(self, constraint_data, slots_per_day: int):
        super().__init__(constraint_data, slots_per_day)

        self.room = constraint_data.get(const.ROOM)
        self.period: Period = Period.from_period_number(
            constraint_data.get(const.PERIOD), slots_per_day
        )
        self.part = constraint_data.get(const.PART)

    def __repr__(self):
        return f"Forbidden Room {self.room} at Period {self.period}"

    # Getter method for 'Room' attribute
    def get_room_name(self) -> str:
        """
        Get the 'Room' attribute.
        Returns:
            str: The name of the room the RoomPeriodConstraint pertains to.
        """
        return self.room

    # Getter method for 'Period' attribute
    def get_period(self) -> Period:
        """
        Get the 'Period' attribute.
        Returns:
            str: The 'Period' value or None if it doesn't exist.
        """
        return self.period

    # Getter method for 'Part' attribute
    def get_part(self) -> str:
        """
        Get the 'Part' attribute.
        Returns:
            str The 'Part' value. This is like the event the constraint refers to
        """
        return self.part


class EventPeriodConstraint(Constraint):
    def __init__(self, constraint_data, slots_per_day: int):
        super().__init__(constraint_data, slots_per_day)

        self.course_name = constraint_data.get(const.COURSE)
        self.period: Period = Period.from_period_number(
            constraint_data.get(const.PERIOD), slots_per_day
        )
        self.exam_ordinal = constraint_data.get(const.EXAM)

        self.part = constraint_data.get(const.PART)

    def get_course_name(self) -> str:
        """
        Get the 'Course' attribute.
        Returns:
            str: The name of the course the event period constraint pertains to.
        """

        return self.course_name

    def __repr__(self):
        if self.part:
            return f"{self.level} {self.course_name} Exam {self.exam_ordinal} - {self.part} at Period {self.period}"
        else:
            return f"{self.level} {self.course_name} Exam {self.exam_ordinal} at Period {self.period}"

    def get_period(self) -> Period:
        """
        Get the 'Period' attribute.
        Returns:
            Optional[str]: The 'Period' value or None if it doesn't exist.
        """

        return self.period

    def get_exam_ordinal(self) -> int:
        """
        Get the 'Exam' attribute.
        Returns:
            Optional[str]: The 'Exam' value or None if it doesn't exist.
        """
        return self.exam_ordinal

    def get_part(self) -> Optional[str]:
        """
        Get the 'Part' attribute.
        Returns:
            str The 'Part' value. This is like the event the constraint refers to.
        """
        return self.part


class EventRoomConstraint(Constraint):
    def __init__(self, constraint_data, slots_per_day: int):
        super().__init__(constraint_data, slots_per_day)

        self.course_name = constraint_data.get(const.COURSE)
        self.room = constraint_data.get(const.ROOM)
        self.part = constraint_data.get(const.PART)

    def get_course_name(self) -> str:
        """
        Get the 'Course' attribute.
        Returns:
            Optional[str]: The 'Course' value or None if it doesn't exist.
        """
        return self.course_name

    def get_room_name(self) -> str:
        """
        Get the 'Room' attribute.
        Returns:
            str: The 'Room' name
        """
        return self.room

    # Getter method for 'Part' attribute
    def get_part(self) -> str:
        """
        Get the 'Part' attribute.
        Returns:
            str The 'Part' value. This is like the event the constraint refers to
        """
        return self.part


class PeriodConstraint(Constraint):
    def __init__(self, constraint_data, slots_per_day: int):
        super().__init__(constraint_data, slots_per_day)

        self.period: Period = Period.from_period_number(
            constraint_data.get(const.PERIOD), slots_per_day
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
        constraint_type = constraint_data.get(const.TYPE)
        if constraint_type is None:
            raise ValueError("Constraint type is missing in constraint_data")

        constraint_constructors = {
            const.ROOM_PERIOD_CONSTRAINT: RoomPeriodConstraint,
            const.EVENT_PERIOD_CONSTRAINT: EventPeriodConstraint,
            const.EVENT_ROOM_CONSTRAINT: EventRoomConstraint,
            const.PERIOD_CONSTRAINT: PeriodConstraint,
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
    def get_room_period_constraints(self) -> Set[RoomPeriodConstraint]:
        return set(constr for constr in self.constraints if constr.is_room_constraint())

    def get_forbidden_room_period_constraints(self) -> Set[RoomPeriodConstraint]:
        return set(
            constr
            for constr in self.constraints
            if constr.is_room_constraint() and constr.is_forbidden()
        )

    def get_undesired_room_period_constraints(self) -> Set[RoomPeriodConstraint]:
        return set(
            constr
            for constr in self.constraints
            if constr.is_room_constraint() and constr.is_undesired()
        )

    def get_preferred_event_period_constraints(self) -> Set[EventPeriodConstraint]:
        """
        Returns a set of preferred event period constraints
        """

        return set(
            constr
            for constr in self.constraints
            if constr.is_event_period_constraint() and constr.is_preferred()
        )

    # Event room Constraiats
    def get_event_room_constraints(self) -> Set[EventRoomConstraint]:
        return set(
            constr for constr in self.constraints if constr.is_event_room_constraint()
        )

    def get_forbidden_event_room_constraints(self) -> Set[EventRoomConstraint]:
        return set(
            constr
            for constr in self.constraints
            if constr.is_event_room_constraint() and constr.is_forbidden()
        )

    def get_undesired_event_room_constraints(self) -> Set[EventRoomConstraint]:
        return set(
            constr
            for constr in self.constraints
            if constr.is_event_room_constraint() and constr.is_undesired()
        )

    # Event period Constraiats
    def get_event_period_constraints(self) -> Set[EventPeriodConstraint]:
        return set(
            constr for constr in self.constraints if constr.is_event_period_constraint()
        )

    def get_forbidden_event_period_constraints(self) -> Set[EventPeriodConstraint]:
        return set(
            constr
            for constr in self.constraints
            if constr.is_event_period_constraint() and constr.is_forbidden()
        )

    def get_undesired_event_period_constraints(self) -> Set[EventPeriodConstraint]:
        return set(
            constr
            for constr in self.constraints
            if constr.is_event_period_constraint() and constr.is_undesired()
        )

    # Period Constraints
    def get_period_constraints(self) -> Set[PeriodConstraint]:
        return set(
            constr for constr in self.constraints if constr.is_period_constraint()
        )

    def get_forbidden_period_constraints(self) -> Set[PeriodConstraint]:
        return set(
            constr
            for constr in self.constraints
            if constr.is_period_constraint() and constr.is_forbidden()
        )

    def get_undesired_period_constraints(self) -> Set[PeriodConstraint]:
        return set(
            constr
            for constr in self.constraints
            if constr.is_period_constraint() and constr.is_undesired()
        )
