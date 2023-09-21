from Constants import *
from typing import ForwardRef


class Event:
    """
    A single Course can have multiple exams. An Exam can have one or more events
    that comprise it. This is what this class defines.
    """

    def __init__(self, examination: "Examination", event_type: str) -> None:
        from Examination import Examination

        self.examination: Examination = examination
        self.event_type: str = event_type

        self.course: Course = examination.get_course()

    def get_examination(self) -> "Examination":
        """
        Returns course that exam event belongs to
        """

        return self.examination

    def get_course(self) -> "Course":
        """
        Returns the course the event belongs to
        """

        return self.examination.get_course()

    def get_course_name(self) -> str:
        """
        Returns the name of the course the examination belongs to
        """

        return self.get_course().get_course_name()

    def get_event_type(self) -> str:
        """
        Returns the type of event
        """

        return self.event_type

    def get_num_rooms(self) -> int:
        """
        Returns the number of rooms requested by the event
        """

        rooms_requested = self.course.get_rooms_requested()
        return rooms_requested.get_number()

    def get_room_type(self) -> str:
        """
        Returns the room type requested by the event
        """

        rooms_requested = self.course.get_rooms_requested()
        return rooms_requested.get_type()

    def __repr__(self) -> str:
        """
        Defines repr method for events
        """

        return (
            f"Event from Examination {self.get_course_name()} of type {self.event_type}"
        )


Examination = ForwardRef("Examination.Examination")
Course = ForwardRef("Course.Course")
