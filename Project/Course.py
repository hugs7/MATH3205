"""
This class handles Courses in the problem
"""


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


class CourseManager:
    def __init__(self):
        self.courses = []

    def add_course(self, course_data):
        new_course = Course(course_data)
        self.courses.append(new_course)

    def __str__(self):
        return "\n".join([str(course) for course in self.courses])
