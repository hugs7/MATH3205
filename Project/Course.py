"""
This class handles Courses in the problem
"""

from typing import List


class Course:
    def __init__(self, course_data):
        self.course = course_data.get("Course")
        self.exam_type = course_data.get("ExamType")
        self.min_distance_between_exams = course_data.get("MinimumDistanceBetweenExams")
        self.num_of_exams = course_data.get("NumberOfExams")
        self.rooms_requested = course_data.get("RoomsRequested")
        self.teacher = course_data.get("Teacher")
        self.written_oral_specs = course_data.get("WrittenOralSpecs")

    def __repr__(self):
        return f"Course: {self.course}, Exam Type: {self.exam_type}, Teacher: {self.teacher}"

    def events(self):
        """
        Create a list of (exam) events for this course, where each event is a
        RoomRequest object
        """
        if self.exam_type == "Written" or self.exam_type == "Oral":
            # All the exams are the same
            return [
                Event(self.course, self.teacher, self.exam_type, self.rooms_requested)
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
                Event(self.course, self.teacher, "Written", self.rooms_requested)
            ]

            # If the oral exam has a room request, add the oral exam with room requested
            # to the courseExams list otherwise, add it with no preferred room
            if room_for_oral:
                courseExams.append(
                    Event(self.course, self.teacher, "Oral", self.rooms_requested)
                )
            else:
                courseExams.append(Event(self.course, self.teacher, "Oral", None))

            # Return the list of courses (should be len = 2)
            return courseExams
        else:
            # There is a case that was not matched rip
            raise Exception("could not match exam type", self.exam_type)


class CourseManager:
    def __init__(self):
        self.courses: List[Course] = []

    def add_course(self, course_data):
        new_course = Course(course_data)
        self.courses.append(new_course)

    def get_courses(self):
        return self.courses

    def __str__(self):
        return "\n".join([str(course) for course in self.courses])


class Event:
    """
    A single Course can have multiple exams. These are defined as "Events"
    Used in the Course.events() method, has members num_rooms and room_type
    """

    def __init__(self, course_name, course_teacher, event_type, rooms_requested_dict):
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

    def __repr__(self):
        return f"course name: {self.course_name}, teacher: {self.course_teacher}, exam type: {self.event_type}, num rooms: {self.num_rooms}, type: {self.room_type}"
