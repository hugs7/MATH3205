"""
This class handles Courses in the problem
Courses are part of curriculums
Courses have examinations
Examinations have Events within them, either Oral, Written or WrittenAndOral
"""

from typing import List

from Examination import Examination
from Constants import *
from Event import Event


class RoomsRequested:
    """
    The RoomsRequested class handles the data about the rooms
    the course has requested for it's exams
    """

    def __init__(self, rooms_requested_data) -> None:
        self.number = rooms_requested_data.get(NUMBER)
        self.type = rooms_requested_data.get(TYPE)

    def get_number(self) -> int:
        """
        Returns the number of rooms requested for each exam
        """

        return self.number

    def get_type(self) -> int:
        """
        Returns the type of the room requested
        """

        return self.type


class WrittenOralSpecs:
    """
    A class to handle the specifications for courses with written and oral examinations
    """

    def __init__(self, written_oral_specs) -> None:
        self.max_distance: int = int(written_oral_specs.get(MAX_DISTANCE))
        self.min_distance: int = int(written_oral_specs.get(MIN_DISTANCE))
        self.room_for_oral: bool = bool(written_oral_specs.get(ROOM_FOR_ORAL))
        self.same_day: bool = bool(written_oral_specs.get(SAME_DAY))

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
        self.course_name = course_data.get(COURSE)

        # Exam type of course
        self.exam_type = course_data.get(EXAM_TYPE)

        # Number of exams the course has
        self.num_of_exams = course_data.get(NUMBER_OF_EXAMS)

        # If NUMBER_OF_EXAMS is more than 1, get MINIMUM_DISTANCE_BETWEEN_EXAMS
        self.min_distance_between_exams = None
        if self.num_of_exams > 1:
            self.min_distance_between_exams = int(
                course_data.get(MINIMUM_DISTANCE_BETWEEN_EXAMS)
            )

        # Rooms requested
        self.rooms_requested: RoomsRequested = RoomsRequested(
            course_data.get(ROOMS_REQUESTED)
        )

        # Teacher
        self.teacher = course_data.get(TEACHER)

        # For courses which have WRITTEN_AND_ORAL exams, get this data
        self.written_oral_specs = None
        if self.is_written_and_oral():
            self.written_oral_specs: WrittenOralSpecs = WrittenOralSpecs(
                course_data.get(WRITTEN_ORAL_SPECS)
            )

        self.examinations: List[Examination] = self._generate_examinations()

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

    def get_examinations(self) -> List[Examination]:
        """
        Returns the list of examinations the course has set
        """

        return self.examinations

    def is_written(self) -> bool:
        """
        Returns true if the course's exams have written events only
        """

        return self.exam_type == WRITTEN

    def is_oral(self) -> bool:
        """
        Returns true if the course's exams have oral events only
        """

        return self.exam_type == ORAL

    def is_written_and_oral(self) -> bool:
        """
        Returns true if the course's exams have written and oral events
        """

        return self.exam_type == WRITTEN_AND_ORAL

    def __repr__(self) -> str:
        """
        repr method for printing out the course's details
        """

        return f"(Course: {self.course_name}, Exam Type: {self.exam_type},  Teacher: {self.teacher})\n"

    def _generate_examinations(self) -> None:
        """
        Create a list of examinations for this course.
        Note that examinations are made up of events.
        Events can be ORAL or WRITTEN.
        Some Examinations have both WRITTEN and ORAL events (strictly in that order)
        while others simple have WRITTEN or ORAL only.
        All examinations for each course have the same type.
        """

        # Consider the cases for WRITTEN OR ORAL separately from WRITTEN_AND_ORAL

        if self.exam_type == WRITTEN or self.exam_type == ORAL:
            # All the exams are the same
            return [
                Examination(
                    self,
                    self.course_name,
                    self.teacher,
                    self.exam_type,
                    self.rooms_requested,
                )
                for _ in range(self.num_of_exams)
            ]
        elif self.exam_type == WRITTEN_AND_ORAL:
            # I'm not sure if this will always hold in larger data sets so this
            # will make the program crash if we need to fix this bit of the
            # code

            # Check number of exams is 2. Given good data, this should never fail
            if self.num_of_exams != 2:
                print(self.num_of_exams)
            assert self.num_of_exams == 2

            # Get what room the oral exam is in
            room_for_oral = self.written_oral_specs["RoomForOral"]

            # Initialise the course exams list with the written exam
            courseExams = [
                Event(
                    self,
                    self.course_name,
                    self.teacher,
                    "Written",
                    self.rooms_requested,
                )
            ]

            # If the oral exam has a room request, add the oral exam with room requested
            # to the courseExams list otherwise, add it with no preferred room
            if room_for_oral:
                courseExams.append(
                    Event(
                        self,
                        self.course_name,
                        self.teacher,
                        "Oral",
                        self.rooms_requested,
                    )
                )
            else:
                courseExams.append(
                    Event(self, self.course_name, self.teacher, "Oral", None)
                )

            # Return the list of courses (should be len = 2)
            return courseExams
        else:
            # There is a case that was not matched rip
            raise Exception("could not match exam type", self.exam_type)


class CourseManager:
    def __init__(self):
        self.courses: list[Course] = []

    def add_course(self, course_data):
        new_course = Course(course_data)
        self.courses.append(new_course)

    def get_courses(self) -> list[Course]:
        return self.courses

    def get_course_by_name(self, course_name: str) -> Course:
        """
        Finds course by name and returns course instance
        """

        for course in self.courses:
            if course.get_course_name() == course_name:
                return course

        raise Exception("Course not found!")

    def get_course_min_distance(self, e1, e2) -> int:
        for course in self.courses:
            if e1 in course.events and e2 in course.events:
                return course.written_oral_specs["MinDistance"]

    def get_course_max_distance(self, e1, e2) -> int:
        for course in self.courses:
            if e1 in course.events and e2 in course.events:
                return course.written_oral_specs["MaxDistance"]

    def get_course_room_for_oral(self, e1, e2) -> int:
        for course in self.courses:
            if e1 in course.events and e2 in course.events:
                return course.written_oral_specs["RoomForOral"]

    def get_course_same_day(self, e1, e2) -> int:
        for course in self.courses:
            if e1 in course.events and e2 in course.events:
                return course.written_oral_specs["SameDay"]

    def __str__(self):
        return "\n".join([str(course) for course in self.courses])
