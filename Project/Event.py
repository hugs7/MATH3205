from typing import ForwardRef

import Constants as const


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

    def room_required(self) -> bool:
        """
        Returns if any room(s) are required for this event
        """

        return not (
            self.get_event_type() == const.ORAL
            and self.get_examination().get_exam_type() == const.WRITTEN_AND_ORAL
            and not self.get_course().get_written_oral_specs().get_room_for_oral()
        )

    def get_num_rooms(self) -> int:
        """
        Returns the number of rooms requested by the event
        """
        if self.room_required():
            return self.course.get_rooms_requested().get_number()
        return 0

    def get_room_type(self) -> str:
        """
        Returns the room type requested by the event
        """
        if self.room_required():
            return self.course.get_rooms_requested().get_type()
        return const.DUMMY

    def __repr__(self) -> str:
        """
        Defines repr method for events
        """

        return f"{self.event_type} Event ({self.get_course_name()} - {self.examination.get_index()})"


Examination = ForwardRef("Examination.Examination")
Course = ForwardRef("Course.Course")
