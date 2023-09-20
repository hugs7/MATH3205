"""
Examinations are exams that a course sets
Each examination has events within it that are like it's components.
Any exam has components WRITTEN, ORAL or WRITTEN_AND_ORAL
"""

from Constants import *
from Event import Event
from typing import List, ForwardRef


class Examination:
    """
    Examinations are set within a course.
    A course can have a number of examinations
    """

    def __init__(self, course: "Course", index: int) -> None:
        """
        Args:
            course: Course object which the examination belongs to
            index: Order that the examination was created in (may be hepful later)

        """

        self.course = course
        self.index = index

        if self.course.is_oral():
            self.exam_type = ORAL
        elif self.course.is_written():
            self.exam_type = WRITTEN
        elif self.course.is_written_and_oral():
            self.exam_type = WRITTEN_AND_ORAL

        # Initialise the events list
        self.events: List[Event] = []

        self.written_event: Event = None
        self.oral_event: Event = None

        # Generate the examination's events upon instantiation
        self._generate_events()

    def get_course(self):
        """
        Returns the course instance the examination belongs to
        """

        return self.course

    def get_index(self) -> int:
        """
        Returns the index of the course
        """

        return self.index

    def get_exam_type(self) -> str:
        """
        Returns the type of examination
        """

        return self.exam_type

    def get_events(self) -> List[Event]:
        """
        Returns the events that comprise the examination
        """

        return self.events

    def get_written_event(self) -> Event:
        """
        Returns Written event if present otherwise None
        """

        return self.written_event

    def get_oral_event(self) -> Event:
        """
        Returns Oral event if present otherwise None
        """

        return self.oral_event

    def _generate_events(self) -> None:
        """
        Generates the events that comprise the examination
        """

        # Consider the cases for WRITTEN OR ORAL separately from WRITTEN_AND_ORAL

        if self.exam_type == WRITTEN:
            self.written_event = Event(self, self.exam_type)
            self.events.append(self.written_event)
        elif self.exam_type == ORAL:
            self.oral_event = Event(self, self.exam_type)
            self.events.append(self.oral_event)
        elif self.exam_type == WRITTEN_AND_ORAL:
            self.written_event = Event(self, self.exam_type)
            self.oral_event = Event(self, self.exam_type)
            self.events.append(self.written_event)
            self.events.append(self.oral_event)

    def get_max_distance(self) -> int:
        """
        If the Examination is of type WRITTEN_AND_ORAL, return the
        maximum distance between the written and oral components.
        Else return None.
        """

        if self.exam_type == WRITTEN_AND_ORAL:
            return self.course.get_written_oral_specs().get_max_distance()

        return None

    def get_min_distance(self) -> int:
        """
        If the Examination is of type WRITTEN_AND_ORAL, return the
        minimum distance between the written and oral components.
        Else return None.
        """

        if self.exam_type == WRITTEN_AND_ORAL:
            return self.course.get_written_oral_specs().get_min_distance()

        return None

    def get_room_for_oral(self) -> bool:
        """
        If the Examination is of type WRITTEN_AND_ORAL, return True
        if the oral component of the examination requires a dedicated room
        Else return None.
        """

        if self.exam_type == WRITTEN_AND_ORAL:
            return self.course.get_written_oral_specs().get_room_for_oral()

        return None

    def get_same_day(self) -> bool:
        """
        If the Examination is of type WRITTEN_AND_ORAL, return True
        if the written and oral events must occur on the same day (hard constraint)
        Else return None.
        """

        if self.exam_type == WRITTEN_AND_ORAL:
            return self.course.get_written_oral_specs().same_day()

        return None

    def __repr__(self) -> str:
        """
        Defines repr method for Examinations
        """

        return f"Examination from course {self.course} of type {self.exam_type}"


Course = ForwardRef("Course.Course")
