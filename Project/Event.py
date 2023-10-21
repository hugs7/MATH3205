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

    def __eq__(self, other: object) -> bool:
        """
        Returns true if event is equal to other event
        """

        if not isinstance(other, Event):
            return False

        return self.examination.__eq__(other.examination) and self.event_type.__eq__(
            other.event_type
        )

    def __hash__(self) -> int:
        """
        Returns hash of event
        """

        return hash((self.examination, self.event_type))

    def get_examination(self) -> "Examination":
        """
        Returns course that exam event belongs to
        """

        return self.examination

    def get_course(self) -> "Course":
        """
        Returns the course the event belongs to
        """
        from Examination import Examination

        examination: Examination = self.get_examination()

        return examination.get_course()

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
        Returns if any room(s) excluding dummy are required for this event
        If the event is oral, no room is required
        If the event is written and a room is
        """
        from Examination import Examination
        from Course import Course, WrittenOralSpecs

        examination: Examination = self.get_examination()
        course: Course = self.get_course()

        if examination.is_written():
            return course.get_rooms_requested().get_number() > 0
        elif examination.is_oral():
            return course.get_rooms_requested().get_number() > 0
        elif examination.is_written_and_oral():
            written_oral_specs: WrittenOralSpecs = course.get_written_oral_specs()
            room_required_for_oral = written_oral_specs.get_room_for_oral()
            return room_required_for_oral

    def get_num_rooms(self) -> int:
        """
        Returns the number of rooms requested by the event
        """

        from Course import Course, RoomsRequested

        course: Course = self.get_course()
        rooms_requested: RoomsRequested = course.get_rooms_requested()

        if self.room_required():
            return rooms_requested.get_number()

        # If no room is required, return 0 (dummy room)
        return 0

    def get_room_type(self) -> str:
        """
        Returns the room type requested by the event
        """

        from Course import Course, RoomsRequested

        course: Course = self.get_course()

        if self.room_required():
            rooms_requested: RoomsRequested = course.get_rooms_requested()
            return rooms_requested.get_type()

        # If no room is required, return dummy
        return const.DUMMY

    def __repr__(self) -> str:
        """
        Defines repr method for events
        """

        event_types = {
            const.WRITTEN: "wr",
            const.ORAL: "or",
            const.WRITTEN_AND_ORAL: "wo",
        }
        room_types = {
            const.DUMMY: "DU",
            const.SMALL: "SM",
            const.MEDIUM: "MD",
            const.LARGE: "LG",
            const.COMPOSITE: "CP",
        }

        return f"{self.get_course_name()}-{self.examination.get_index()} ({event_types[self.event_type]}, {self.get_num_rooms()}x{room_types.get(self.get_room_type(), self.get_room_type())})"


Examination = ForwardRef("Examination.Examination")
Course = ForwardRef("Course.Course")
