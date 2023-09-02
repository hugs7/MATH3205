"""
Class for handing rooms in the problem
"""

from typing import List


class Room:
    def __init__(self, room_data):
        self.room = room_data.get("Room")
        self.type = room_data.get("Type")
        self.members = room_data.get("Members", [])

    def __repr__(self):
        return f"Room {self.room} - Type: {self.type}, Members: {', '.join(self.members)}\n"

    def get_room(self):
        return self.room

    def get_type(self):
        return self.type

    def get_members(self):
        return self.members


class RoomManager:
    def __init__(self):
        # rooms is a list of Room objects
        self.rooms: List[Room] = []

    def add_room(self, room_data):
        # Check if room already exists
        existing_room = self.get_room_by_name(room_data.get("Room"))
        if existing_room is not None:
            raise ValueError("Room already exists")

        new_room = Room(room_data)
        self.rooms.append(new_room)

    def get_rooms(self):
        return self.rooms

    def get_room_by_name(self, room_name):
        for room in self.rooms:
            if room.get_room() == room_name:
                return room
        return None

    def get_rooms_by_type(self, room_type):
        matching_rooms = []
        for room in self.rooms:
            if room.get_type() == room_type:
                matching_rooms.append(room)
        return matching_rooms

    def get_composite_rooms(self):
        # Gets a subset of self.rooms which are composite
        # Begin with an empty list
        composite_rooms: List[Room] = []

        # Iterate over all rooms
        for room in self.rooms:
            if room.get_type() == "Composite":
                composite_rooms.append(room)
        return composite_rooms

    # Implement the iterable functionality
    def __iter__(self):
        return iter(self.rooms)
