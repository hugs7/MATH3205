"""
This class handles Courses in the problem
Courses are part of curriculums
Courses have examinations
Examinations have Events within them, either Oral, Written or WrittenAndOral
"""

from typing import List
import Constants as const
from Examination import Examination


class RoomsRequested:
    """
    The RoomsRequested class handles the data about the rooms
    the course has requested for it's exams
    """

    def __init__(self, rooms_requested_data) -> None:
        self.number = rooms_requested_data.get(const.NUMBER)
        self.type = rooms_requested_data.get(const.TYPE)

    def get_number(self) -> int:
        """
        Returns the number of rooms requested for each exam
        """

        return self.number

    def get_type(self) -> str:
        """
        Returns the type of the room requested. When the event is to be held in
        multiple rooms (composite), the type returned is small, medium or large not composite
        """

        return self.type


class WrittenOralSpecs:
    """
    A class to handle the specifications for courses with written and oral examinations
    """

    def __init__(self, written_oral_specs) -> None:
        self.max_distance: int = int(written_oral_specs.get(const.MAX_DISTANCE))
        self.min_distance: int = int(written_oral_specs.get(const.MIN_DISTANCE))
        self.room_for_oral: bool = bool(written_oral_specs.get(const.ROOM_FOR_ORAL))
        self.same_day: bool = bool(written_oral_specs.get(const.SAME_DAY))

    def __repr__(self) -> str:
        """
        Representation method for WrittenOralSpecs
        """

        return f"WOS: ({self.min_distance} - {self.max_distance}), ({self.room_for_oral}, {self.same_day})"

    def get_max_distance(self) -> int:
        """
        Returns the maximum distance between the written and oral events within the examination
        """

        return self.max_distance

    def get_min_distance(self) -> int:
        """
        Returns the maximum distance between the written and oral events within the examination
        """

        return self.min_distance

    def get_room_for_oral(self) -> bool:
        """
        Returns true if the oral event of the examination requires a room
        """

        return self.room_for_oral

    def get_same_day(self) -> bool:
        """
        Returns true if the oral event of the examination must occur on the same
        day as the written event of the same examination
        """

        return self.same_day


class Course:
    """
    The Course class defines the course object for each course
    taught by the university.
    """

    def __init__(self, course_data) -> None:
        # Course name
        self.course_name = course_data.get(const.COURSE)

        # Exam type of course
        self.exam_type = course_data.get(const.EXAM_TYPE)

        # Number of exams the course has
        self.num_of_exams = course_data.get(const.NUMBER_OF_EXAMS)

        # If NUMBER_OF_EXAMS is more than 1, get MINIMUM_DISTANCE_BETWEEN_EXAMS
        self.min_distance_between_exams = None
        if self.num_of_exams > 1:
            self.min_distance_between_exams = int(
                course_data.get(const.MINIMUM_DISTANCE_BETWEEN_EXAMS)
            )

        # Rooms requested
        self.rooms_requested: RoomsRequested = RoomsRequested(
            course_data.get(const.ROOMS_REQUESTED)
        )

        # Teacher
        self.teacher = course_data.get(const.TEACHER)

        # For courses which have WRITTEN_AND_ORAL exams, get this data
        if self.is_written_and_oral():
            self.written_oral_specs: WrittenOralSpecs = WrittenOralSpecs(
                course_data.get(const.WRITTEN_ORAL_SPECS)
            )

        self.examinations: List[Examination] = []
        self._generate_examinations()

    def get_course_name(self) -> str:
        """
        Returns the name of the course
        """

        return self.course_name

    def get_teacher(self) -> str:
        """
        Returns the teacher of the course
        """

        return self.teacher

    def get_exam_type(self) -> str:
        """
        Returns the exam type of the course
        Either WRITTEN, ORAL, or WRITTEN_AND_ORAL
        """

        return self.exam_type

    def get_min_distance_between_exams(self) -> int:
        """
        Returns the number of timeslots between exams
        Returns None if the course has only 1 exam.
        """

        if self.num_of_exams == 1:
            return None

        return self.min_distance_between_exams

    def get_written_oral_specs(self) -> WrittenOralSpecs:
        """
        Returns written_oral_specs if the exam type is WRITTEN_AND_ORAL.
        Otherwise returns None.
        """

        if self.is_written_and_oral():
            return self.written_oral_specs

        return None

    def get_rooms_requested(self) -> RoomsRequested:
        """
        Returns the rooms requested of the Course
        """

        return self.rooms_requested

    def get_examinations(self) -> List[Examination]:
        """
        Returns the list of examinations the course has set
        """

        return self.examinations

    def is_written(self) -> bool:
        """
        Returns true if the course's exams have written events only
        """

        return self.exam_type == const.WRITTEN

    def is_oral(self) -> bool:
        """
        Returns true if the course's exams have oral events only
        """

        return self.exam_type == const.ORAL

    def is_written_and_oral(self) -> bool:
        """
        Returns true if the course's exams have written and oral events
        """

        return self.exam_type == const.WRITTEN_AND_ORAL

    def __repr__(self) -> str:
        """
        repr method for printing out the course's details
        """

        return f"(Course: {self.course_name}, Exam Type: {self.exam_type},  Teacher: {self.teacher})"

    def __hash__(self):
        """
        Compute the hash value of the Course object based on the course_name.
        """

        return hash(self.course_name)

    def __eq__(self, other):
        """
        Compare two Course objects for equality based on the course_name.
        """

        if isinstance(other, Course):
            return self.course_name == other.course_name
        return False

    def _generate_examinations(self) -> None:
        """
        Create a list of examinations for this course.
        Note that examinations are made up of events.
        Events can be ORAL or WRITTEN.
        Some Examinations have both WRITTEN and ORAL events (strictly in that order)
        while others simple have WRITTEN or ORAL only.
        All examinations for each course have the same type.
        """

        # Create an Examination object for the number of exams specified
        for exam_index in range(self.num_of_exams):
            self.examinations.append(Examination(self, exam_index))


class CourseManager:
    """
    Manages the courses the university runs
    """

    def __init__(self) -> None:
        self.courses: List[Course] = []

    def add_course(self, course_data) -> Course:
        """
        Adds a course to the course manager and returns the course
        """

        new_course = Course(course_data)
        self.courses.append(new_course)

        return new_course

    def get_courses(self) -> List[Course]:
        """
        Returns a list of the courses the CourseManager manages
        """

        return self.courses

    def get_course_by_name(self, course_name: str) -> Course:
        """
        Finds course by name and returns course instance
        Raises a CourseNotFoundException if the course is not managed by
        this CourseManager
        """

        for course in self.courses:
            if course.get_course_name() == course_name:
                return course

        raise CourseNotFoundException("Course not found!")

    def __str__(self):
        return "\n".join([str(course) for course in self.courses])


class CourseNotFoundException(Exception):
    """
    Defines an exception for course not found
    """

    def __init__(self, exp_msg: str) -> None:
        super().__init__(exp_msg)
