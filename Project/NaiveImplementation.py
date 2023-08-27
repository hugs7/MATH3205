"""
This file defines a naive implementation for the Exam timetabling problem

Hugo Burton
27/08/2023
"""

from gurobipy import Model, quicksum, GRB
import json  # For importing the data as JSON format

from Room import Room, RoomManager

# Import data
data_file = ".\\Project\\testData.json"

with open(data_file, "r") as json_file:
    json_data = json_file.read()

# print(json_data)
parsed_data = json.loads(json_data)

# Separate out data

# Exam schedule constraints
constraints = parsed_data["Constraints"]

# Courses
courses = parsed_data["Courses"]
print(courses)
# Curricula
curricula = parsed_data["Curricula"]

# Time Periods
periods = parsed_data["Periods"]

# Exam Distance
primaryPrimaryDistance = parsed_data["PrimaryPrimaryDistance"]

# Rooms
rooms = parsed_data["Rooms"]
roomManager = RoomManager()
for room in rooms:
    roomManager.add_room(room)

# Time slots
slotsPerDay = parsed_data["SlotsPerDay"]

# --- Define Model ---
m = Model("Uni Exams")

# Sets
teachers = parsed_data["Teachers"]
rooms = roomManager


# Data


# Variables


# Objective Function
# m.setObjective(0, GRB.MAXIMIZE)

# Print output

# print("Objective Value:", m.ObjVal)
