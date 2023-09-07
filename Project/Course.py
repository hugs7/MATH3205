"""
This class handles Courses in the problem
"""

from typing import List


class Course:
    def __init__(self, course_data):
        self.course_name = course_data.get("Course")
        self.exam_type = course_data.get("ExamType")

        if course_data.get("MinimumDistanceBetweenExams") is not None:
            self.min_distance_between_exams = int(
                course_data.get("MinimumDistanceBetweenExams")
            )
        else:
            self.min_distance_between_exams = None
        self.num_of_exams = course_data.get("NumberOfExams")
        self.rooms_requested = course_data.get("RoomsRequested")
        self.teacher = course_data.get("Teacher")
        self.written_oral_specs = course_data.get("WrittenOralSpecs")

        self.events = self._generate_events()

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
        Either Written, Oral, or WrittenAndOral
        """

        return self.exam_type

    def get_min_distance_between_exams(self) -> int:
        """
        Returns the number of timeslots between exams
        """

        return self.min_distance_between_exams

    def get_events(self) -> List["Event"]:
        return self.events
    
    def __repr__(self):
        return f"(Course: {self.course_name}, Exam Type: {self.exam_type}, Teacher: {self.teacher})\n"

    def _generate_events(self):
        """
        Create a list of (exam) events for this course, where each event is a
        RoomRequest object
        """
        if self.exam_type == "Written" or self.exam_type == "Oral":
            # All the exams are the same
            return [
                Event(
                    self,
                    self.course_name,
                    self.teacher,
                    self.exam_type,
                    self.rooms_requested,
                )
                for _ in range(self.num_of_exams)
            ]
        elif self.exam_type == "WrittenAndOral":
            # I'm not sure if this will always hold in larger data sets so this
            # will make the program crash if we need to fix this bit of the
            # code

            # Check number of exams is 2. Given good data, this should never fail
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

    def __str__(self):
        return "\n".join([str(course) for course in self.courses])


class Event:
    """
    A single Course can have multiple exams. These are defined as "Events"
    Used in the Course.events() method, has members num_rooms and room_type
    """

    def __init__(
        self, course, course_name, course_teacher, event_type, rooms_requested_dict
    ):
        self.course: Course = course
        self.event_type = event_type
        self.course_name = course_name
        self.course_teacher = course_teacher
        if rooms_requested_dict is None:
            self.num_rooms = 0
            self.room_type = None
        else:
            self.num_rooms = rooms_requested_dict["Number"]
            if "Type" in rooms_requested_dict:
                self.room_type = rooms_requested_dict["Type"]
            else:
                self.room_type = None

    def get_course(self) -> Course:
        """
        Returns course that exam event belongs to
        """

        return self.course

    def __repr__(self):
        return f"{self.course_name} ({self.event_type})"
