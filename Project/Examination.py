"""
Examinations are exams that a course sets
Each examination has events within it that are like it's components.
Any exam has components WRITTEN, ORAL or WRITTEN_AND_ORAL
"""

from Constants import *
from Course import Course
from Event import Event
from typing import List


class Examination:
    """
    Examinations are set within a course.
    A course can have a number of examinations
    """

    def __init__(self, course: Course) -> None:
        """
        Args:
            course: Course object which the examination belongs to

        """

        self.course = course

        if self.course.is_oral():
            self.exam_type = ORAL
        elif self.course.is_written():
            self.exam_type = WRITTEN
        elif self.course.is_written_and_oral():
            self.exam_type = WRITTEN_AND_ORAL

        # Initialise the events list
        self.events: List[Event] = []

    def get_course(self) -> Course:
        """
        Returns the course instance the examination belongs to
        """

        return self.course

    def get_exam_type(self) -> str:
        """
        Returns the type of examination
        """

        return self.exam_type

    def _generate_events(self) -> None:
        """
        Generates the events that comprise the examination
        """

        # Consider the cases for WRITTEN OR ORAL separately from WRITTEN_AND_ORAL

        if self.exam_type == WRITTEN or self.exam_type == ORAL:
            single_event = Event(self, self.exam_type)
            self.events.append(single_event)

    def __repr__(self) -> str:
        """
        Defines repr method for Examinations
        """

        return f"Examination from course {self.course} of type {self.exam_type}"
