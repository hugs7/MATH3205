"""
Class for handing rooms in the problem
"""

# Constants

from typing import Iterator


COMPOSITE = "Composite"
LARGE = "Large"
SMALL = "Small"
DUMMY = "Dummy"


class Room:
    def __init__(self, room_data=None):
        if room_data is None:
            self.room = DUMMY
            self.room_type = DUMMY
            self.members = []
        else:
            self.room = room_data.get("Room")
            self.room_type = room_data.get("Type")
            self.members = room_data.get("Members", [])

    def __repr__(self) -> str:
        return f"Room {self.room} - Type: {self.room_type}, Members: {', '.join(self.members)}\n"

    def get_room(self) -> str:
        """
        Returns name of room
        """

        return self.room

    def get_type(self) -> str:
        """
        Returns type of room
        """

        return self.room_type

    def get_members(self) -> list[str]:
        """
        Returns members of the room as list of strings.
        If room is not composite, throws error
        """

        if not self.is_composite():
            raise Exception("Room is not composite")

        return self.members

    def is_composite(self) -> bool:
        """
        Returns true if room is composite
        False otherwise
        """

        return self.type == COMPOSITE

    def is_small(self) -> bool:
        """
        Returns true if room is small
        False otherwise
        """

        return self.type == SMALL

    def is_large(self) -> bool:
        """
        Returns true if room is large
        False otherwise
        """

        return self.type == LARGE


class RoomManager:
    """
    RoomManager handles all the rooms for the exam scheduling problem. This includes small, large and composite rooms.
    As well as the dummy room for exams not assigned a room
    """

    def __init__(self):
        """
        Inititialisation method for RoomManager. No required arguments
        """

        # List of rooms the RoomManager Stores
        self.rooms: list[Room] = [Room()]

        # Graph in the form of an ajacency list for storing joining rooms
        self.composite_map = {}

        # Flag for if Composite room graph has been constructed
        self.constructed = False

    def add_room(self, room_data: any) -> Room:
        """
        Creates room and returns it to the caller
        """

        assert not self.constructed
        # Check if room already exists
        existing_room = self.get_room_by_name(room_data.get("Room"))
        if existing_room is not None:
            raise ValueError("Room already exists")

        new_room = Room(room_data)
        self.rooms.append(new_room)

        return new_room

    def get_rooms(self) -> list[Room]:
        """
        Gets list of rooms stored by the RoomManager
        """

        return self.rooms

    def get_room_by_name(self, room_name: str) -> Room | None:
        """
        Gets room by it's name
        """

        for room in self.rooms:
            if room.get_room() == room_name:
                return room
        return None

    def get_composite_rooms(self) -> list[Room]:
        """
        Gets list of composite rooms stored by the RoomManager
        """

        return [
            r for r in self.rooms if r.get_type() == COMPOSITE and r.get_type != DUMMY
        ]

    def get_single_rooms(self) -> list[Room]:
        """
        Gets list of non-composite (small and large) rooms stored by the RoomManager
        """

        return [
            r for r in self.rooms if r.get_type() != COMPOSITE and r.get_type != DUMMY
        ]

    def get_dummy_room(self) -> Room:
        """
        Returns dummy room
        """

        for r in self.rooms:
            if r.get_type() == DUMMY:
                return r
        raise Exception("No dummy room big sad")

    def construct_composite_map(self) -> dict[Room, list[Room]]:
        """
        Constructs graph in the form of an ajacency list to store
        which rooms are composite and joining
        """

        assert not self.constructed

        # Iterate over all composite rooms stored by the RoomManager
        for compRoom in self.get_composite_rooms():
            # Get the members of compRoom (as string)
            members = compRoom.get_members()

            # Create ajacency list (a dictionary with values of a list[Room])
            self.composite_map[compRoom] = frozenset(
                self.get_room_by_name(r) for r in members
            )

        # Set the constructed flag to true
        self.constructed = True

        # Return Composite Graph
        return self.composite_map

    def get_room_overlap(self) -> list[str]:
        rooms = []
        overlap = []
        for comp_room in self.get_composite_rooms():
            for room in comp_room.get_members():
                if room in rooms:
                    overlap.append(room)
                else:
                    rooms.append(room)
        return overlap

    def get_overlap(self, Room: Room) -> list[Room]:
        overlap = []
        for room in Room.get_members():
            if room in self.get_room_overlap():
                overlap.append(room)
        return overlap

    # Implement the iterable functionality
    def __iter__(self) -> Iterator[Room]:
        return iter(self.rooms)
