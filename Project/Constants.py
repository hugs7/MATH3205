"""
Constants file
"""

GUROBI = "Gurobi"
UNIVERSITY_EXAMINATIONS = "University Examinations"

CONSTRAINTS = "Constraints"
COURSES = "Courses"
CURRICULA = "Curricula"
ROOMS = "Rooms"
PERIODS = "Periods"
PERIOD = "Period"
PART = "Part"

SECONDS = "seconds"

COURSE = "Course"
NUMBER_OF_EXAMS = "NumberOfExams"
EXAM = "Exam"
LEVEL = "Level"

# Exam types
EXAM_TYPE = "ExamType"
WRITTEN_AND_ORAL = "WrittenAndOral"
ORAL = "Oral"
WRITTEN = "Written"
WRITTEN_ORAL_SPECS = "WrittenOralSpecs"

MINIMUM_DISTANCE_BETWEEN_EXAMS = "MinimumDistanceBetweenExams"

ROOMS_REQUESTED = "RoomsRequested"

TEACHER = "Teacher"
TEACHERS = "Teachers"


# Written Oral Specs
MAX_DISTANCE = "MaxDistance"
MIN_DISTANCE = "MinDistance"
ROOM_FOR_ORAL = "RoomForOral"
SAME_DAY = "SameDay"


# Timeslots
SLOTS_PER_DAY = "SlotsPerDay"

PRIMARY_PRIMARY_DISTANCE = "PrimaryPrimaryDistance"
PRIMARY_SSECONDARY_DISTANCE = "PrimarySecondaryDistance"

# --- Rooms ---

ROOM = "Room"
COMPOSITE = "Composite"
LARGE = "Large"
MEDIUM = "Medium"
SMALL = "Small"
DUMMY = "Dummy"
MEMBERS = "Members"

# Rooms Requested
NUMBER = "Number"
TYPE = "Type"
# ------ Weights of Soft Constraints ------
# S1 soft conflicts
SC_PRIMARY_SECONDARY = 5
SC_SECONDARY_SECONDARY = 1

# S2 preferences
P_UNDESIRED_PERIOD = 10
P_NOT_PREFERED_ROOM = 2
P_UNDESIRED_ROOM = 5

# S3 directed and undirected distance
DD_SAME_EXAMINATION = 15
DD_SAME_COURSE = 12
UD_PRIMARY_PRIMARY = 2
UD_PRIMARY_SECONDARY = 2
