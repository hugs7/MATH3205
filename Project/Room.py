"""
Class for handing rooms in the problem
"""

# Constants

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

    def get_type(self):
        """
        Returns type of room
        """

        return self.room_type

    def get_members(self) -> list[str]:
        """
        Returns members of the room as list of strings.
        If room is not composite, throws error
        """

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
    def __init__(self):
        # rooms is a list of Room objects; initialise collection of all rooms
        # so that it contains the dummy room
        self.rooms: list[Room] = [Room()]
        self.composite_map = {}
        self.constructed = False

    def add_room(self, room_data) -> Room:
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
        return self.rooms

    def get_room_by_name(self, room_name):
        for room in self.rooms:
            if room.get_room() == room_name:
                return room
        return None

    def get_composite_rooms(self) -> list[Room]:
        return [r for r in self.rooms if r.get_type() == COMPOSITE]

    def get_single_rooms(self) -> list[Room]:
        return [
            r for r in self.rooms if r.get_type() != COMPOSITE and r.get_type != DUMMY
        ]

    def get_dummy_room(self):
        for r in self.rooms:
            if r.get_type() == DUMMY:
                return r
        raise Exception("no dummy room big sad")

    def construct_composite_map(self):
        assert not self.constructed
        self.constructed = True
        for comp in self.get_rooms():
            if comp.get_type() == COMPOSITE:
                members = comp.get_members()
                self.composite_map[comp] = frozenset(
                    self.get_room_by_name(r) for r in members
                )

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
    def __iter__(self):
        return iter(self.rooms)
