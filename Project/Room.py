"""
Class for handing rooms in the problem
"""

from typing import List


class Room:
    def __init__(self, room_data=None):
        if room_data is None:
            self.room = "Dummy"
            self.room_type = "Dummy"
            self.members = []
        else:
            self.room = room_data.get("Room")
            self.room_type = room_data.get("Type")
            self.members = room_data.get("Members", [])

    def __repr__(self):
        return f"Room {self.room} - Type: {self.room_type}, Members: {', '.join(self.members)}\n"

    def get_room(self):
        return self.room

    def get_type(self):
        return self.room_type

    def get_members(self):
        return self.members


class RoomManager:
    def __init__(self):
        # rooms is a list of Room objects; initialise collection of all rooms
        # so that it contains the dummy room
        self.rooms: List[Room] = [Room()]
        self.composite_map = {}
        self.constructed = False

    def add_room(self, room_data):
        assert not self.constructed
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

    def get_composite_rooms(self):
        return [r for r in self.rooms if r.get_type() == "Composite"]

    def get_single_rooms(self):
        return [
            r
            for r in self.rooms
            if r.get_type() != "Composite" and r.get_type != "Dummy"
        ]

    def get_dummy_room(self):
        for r in self.rooms:
            if r.get_type() == "Dummy":
                return r
        raise Exception("no dummy room big sad")

    def construct_composite_map(self):
        assert not self.constructed
        self.constructed = True
        for comp in self.get_rooms():
            if comp.get_type() == "Composite":
                members = comp.get_members()
                self.composite_map[comp] = frozenset(
                    self.get_room_by_name(r) for r in members
                )

    def get_room_overlap(self) -> List[str]:
        rooms = []
        overlap = []
        for comp_room in self.get_composite_rooms():
            for room in comp_room.get_members():
                if room in rooms:
                    overlap.append(room)
                else:
                    rooms.append(room)
        return overlap

    def get_overlap(self, Room: Room) -> List[Room]:
        overlap = []
        for room in Room.get_members():
            if room in self.get_room_overlap():
                overlap.append(room)
        return overlap

    # Implement the iterable functionality
    def __iter__(self):
        return iter(self.rooms)
