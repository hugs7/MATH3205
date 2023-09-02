"""
Class for handing rooms in the problem
"""


class Room:
    def __init__(self, room_data):
        self.room = room_data.get("Room")
        self.type = room_data.get("Type")
        self.members = room_data.get("Members", [])

    def __repr__(self):
        return f"Room {self.room} - Type: {self.type}, Members: {', '.join(self.members)}\n"


class RoomManager:
    def __init__(self):
        self.rooms = []

    def add_room(self, room_data):
        new_room = Room(room_data)
        self.rooms.append(new_room)

    def get_rooms(self):
        return self.rooms

    def get_room_by_name(self, room_name):
        for room in self.rooms:
            if room.room == room_name:
                return room
        return None

    def get_rooms_by_type(self, room_type):
        matching_rooms = []
        for room in self.rooms:
            if room.type == room_type:
                matching_rooms.append(room)
        return matching_rooms

    def get_composite_rooms(self) -> list(Room):
        composite_rooms = []
        for room in self.rooms:
            if room.type == "Composite":
                composite_rooms.append(room)
        return composite_rooms

    @staticmethod
    def get_composite_room_members(compositeRoom: list(Room)):
        """
        Returns a list of individual rooms which make up the compositeRoom
        """

        members = []
        for room in compositeRoom:
            members.append(room.room)

        return members


# # Example data
# data = {
#     "Rooms": [
#         {"Room": "A", "Type": "Large"},
#         {"Room": "B", "Type": "Large"},
#         # ... (other room data)
#     ]
# }

# room_manager = RoomManager()

# # Add rooms to the RoomManager
# for room_data in data["Rooms"]:
#     room_manager.add_room(room_data)

# # Accessing rooms and their properties
# room_A = room_manager.get_room_by_name("A")
# large_rooms = room_manager.get_rooms_by_type("Large")
# composite_rooms = room_manager.get_composite_rooms()

# print(room_A.room, room_A.type, room_A.members)
# for room in large_rooms:
#     print(room.room, room.type)
# for room in composite_rooms:
#     print(room.room, room.type, room.members)
