"""
Class for handing rooms in the problem
"""

import Constants as const
from typing import Iterator, Dict, List


class Room:
    def __init__(self, room_data=None) -> None:
        if room_data is None:
            self.room = const.DUMMY
            self.room_type = const.DUMMY
            self.members = []
        else:
            self.room = room_data.get(const.ROOM)
            self.room_type = room_data.get(const.TYPE)
            self.members = room_data.get(const.MEMBERS, [])

    def __repr__(self) -> str:
        return f"{self.room} ({self.room_type})"

    def get_room(self) -> str:
        """
        Returns name of room
        """

        return self.room

    def get_type(self) -> str:
        """
        Returns type of room SMALL, MEDIUM, LARGE or COMPOSITE
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

        return self.room_type == const.COMPOSITE

    def is_small(self) -> bool:
        """
        Returns true if room is small
        False otherwise
        """

        return self.room_type == const.SMALL

    def is_medium(self) -> bool:
        """
        Returns true if room is medium
        False otherwise
        """

        return self.room_type == const.MEDIUM

    def is_large(self) -> bool:
        """
        Returns true if room is large
        False otherwise
        """

        return self.room_type == const.LARGE


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
        self.composite_map: Dict[Room, List[Room]] = {}

        # Flag for if Composite room graph has been constructed
        self.constructed = False

    def add_room(self, room_data: any) -> Room:
        """
        Creates room and returns it to the caller
        """

        assert not self.constructed
        # Check if room already exists
        existing_room = self.get_room_by_name(room_data.get(const.ROOM))
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

    def get_room_by_name(self, room_name: str) -> Room:
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

        return [r for r in self.rooms if r.get_type() == const.COMPOSITE]

    def get_single_rooms(self) -> list[Room]:
        """
        Gets list of non-composite (small, medium and large) rooms stored by the RoomManager
        """

        return [
            r
            for r in self.rooms
            if r.get_type() != const.COMPOSITE and r.get_type() != const.DUMMY
        ]

    def get_small_rooms(self) -> list[Room]:
        """
        Gets list of small rooms stored by the RoomManager
        """

        return [r for r in self.rooms if r.get_type() == const.SMALL]

    def get_medium_rooms(self) -> list[Room]:
        """
        Gets list of medium rooms stored by the RoomManager
        """

        return [r for r in self.rooms if r.get_type() == const.MEDIUM]

    def get_large_rooms(self) -> list[Room]:
        """
        Gets list of large rooms stored by the RoomManager
        """

        return [r for r in self.rooms if r.get_type() == const.LARGE]

    def get_single_rooms_by_type(self, room_type: str) -> list[Room]:
        """
        Gets list of single rooms of a given type stored by the RoomManager
        """

        return [r for r in self.rooms if r.get_type() == room_type]

    def get_dummy_room(self) -> Room:
        """
        Returns dummy room
        """

        for r in self.rooms:
            if r.get_type() == const.DUMMY:
                return r
        raise Exception("No dummy room big sad")

    def construct_composite_map(self) -> Dict[Room, List[Room]]:
        """
        Constructs graph in the form of an ajacency list to store
        which rooms are composite and joining
        """

        if self.constructed:
            return self.composite_map

        # Iterate over all composite rooms stored by the RoomManager
        for comp_room in self.get_composite_rooms():
            # Get the members of compRoom (as string)
            members = comp_room.get_members()

            # Create ajacency list (a dictionary with values of a list[Room])
            self.composite_map[comp_room]: Dict[Room, List[Room]] = [
                self.get_room_by_name(r) for r in members
            ]

        # Set the constructed flag to true
        self.constructed = True

        # Return Composite Graph
        return self.composite_map

    def get_overlapping_rooms(self) -> Dict[Room, List[Room]]:
        """
        Returns a dictionary with composite rooms as keys and
        a list of overlapping rooms as values.
        """

        if not self.constructed:
            self.construct_composite_map()

        overlapping_rooms: Dict[Room, List[Room]] = {}

        visited_regions = []
        for comp_room, members in self.composite_map.items():
            rooms_in_connected_region = [comp_room]
            if comp_room in visited_regions:
                continue
            visited_regions.append(comp_room)

            connected_region: Dict[Room, List[Room]] = {}
            connected_region[comp_room] = members

            for other_comp_room, other_members in self.composite_map.items():
                if comp_room == other_comp_room:
                    continue

                connected = False
                for other_member in other_members:
                    if other_member in members:
                        connected = True
                        break

                if not connected:
                    continue

                rooms_in_connected_region.append(other_comp_room)
                visited_regions.append(other_comp_room)
                connected_region[other_comp_room] = other_members

            connected_region_set_of_members = [
                set(members) for members in connected_region.values()
            ]

            intersection = connected_region_set_of_members[0]
            for cr in connected_region_set_of_members[1:]:
                intersection = intersection.intersection(cr)

            for room in rooms_in_connected_region:
                overlapping_rooms[room] = list(intersection)

        return overlapping_rooms

    # Implement the iterable functionality
    def __iter__(self) -> Iterator[Room]:
        return iter(self.rooms)

    def __repr__(self) -> str:
        """
        Repr method for RoomManager
        """

        string = "Room Manager: \n"
        for room in self.rooms:
            string += f"{room}\n"
        return string
