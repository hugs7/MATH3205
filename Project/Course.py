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

    def events(self):
        """
        Create a list of (exam) events for this course, where each event is a
        RoomRequest object
        """
        if self.exam_type == "Written" or self.exam_type == "Oral":
            # All the exams are the same
            return [RoomRequest(self.rooms_requested) for _ in range(self.num_of_exams)]
        elif self.exam_type == "WrittenAndOral":
            # I'm not sure if this will always hold in larger data sets so this
            # will make the program crash if we need to fix this bit of the
            # code
            assert self.num_of_exams == 2
            room_for_oral = self.written_oral_specs["RoomForOral"]
            res = [RoomRequest(self.rooms_requested)]
            if room_for_oral:
                res.append(RoomRequest(self.rooms_requested))
            else:
                res.append(RoomRequest(None))
            return res
        else:
            # There is a case that was not matched rip
            raise Exception("could not match exam type", self.exam_type)


class CourseManager:
    def __init__(self):
        self.courses = []

    def add_course(self, course_data):
        new_course = Course(course_data)
        self.courses.append(new_course)

    def __str__(self):
        return "\n".join([str(course) for course in self.courses])


class RoomRequest:
    """
    Used in the Course.events() method, has members num_rooms and room_type
    """

    def __init__(self, rooms_requested_dict):
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
        return f"num_rooms: {self.num_rooms}, type: {self.room_type}"
