"""
Class for handing rooms in the problem
"""

import Constants as const
from typing import Iterator, Dict, List, Tuple


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
        """
        Repr method for Room
        """

        if self.is_composite():
            return f"{self.room} ({self.room_type}) - {self.members}"

        return f"{self.room} ({self.room_type})"

    def __eq__(self, __value: object) -> bool:
        """
        Returns true if room is equal to other room
        """

        if not isinstance(__value, Room):
            return False

        return self.room == __value.room

    def __hash__(self) -> int:
        """
        Returns hash of room
        """

        return hash(self.room)

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

    def get_num_members(self) -> int:
        """
        Returns number of members in room
        """

        if not self.is_composite():
            return 1

        return len(self.members)

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
    RoomManager handles all the rooms for the exam scheduling problem.
    This includes small, large and composite rooms. As well as the dummy
    room for exams not assigned a room
    """

    def __init__(self):
        """
        Inititialisation method for RoomManager. No required arguments
        """

        # List of rooms the RoomManager Stores
        # Add the dummy room
        self.rooms: list[Room] = [Room()]

        # Graph in the form of an ajacency list for storing joining rooms
        self.composite_map: Dict[Room, List[Room]] = {}

        # Flag for if Composite room graph has been constructed
        self.constructed = False

        self.room_joining_map: Dict[Room, List[Room]] = {}
        self.construct_joining_map()

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

    def get_rooms_by_size(self) -> Dict[str, List[Room]]:
        """
        Gets list of all rooms stored by the RoomManager grouped by size and
        number of members in a dictionary.
        """

        rooms_by_type_and_size: Dict[Tuple[str, int], List[Room]] = {}

        for room_type in const.ROOM_TYPES:
            rooms = self.get_rooms()
            for room in rooms:
                if room.is_composite():
                    room_members = room.get_members()

                    # Can just use the first room to get size given all rooms in composite room
                    # are the same size (homogeneous)
                    room_member_type = self.get_room_by_name(room_members[0]).get_type()

                    num_room_members = len(room_members)
                else:
                    num_room_members = 1
                    room_member_type = room.get_type()

                if (room_type, num_room_members) not in rooms_by_type_and_size.keys():
                    rooms_by_type_and_size[(room_type, num_room_members)] = []

                if room_member_type != room_type:
                    continue

                rooms_by_type_and_size[(room_member_type, num_room_members)].append(
                    room
                )

        return rooms_by_type_and_size

    def get_rooms_by_size_and_num_rooms(
        self, room_type: str, num_rooms: int
    ) -> List[Room]:
        """
        Gets list of rooms stored by the RoomManager given a room type and number of room members
        number of room members = 1 => single room
        number of room members > 1 => composite room
        """

        get_rooms_by_type_and_size = self.get_rooms_by_size()

        return get_rooms_by_type_and_size.get((room_type, num_rooms), [])

    def get_max_members_by_room_type(self) -> Dict[str, int]:
        """
        Returns the maximum number of memers in a room by room type in a dictionary
        1 if only single rooms of that room_type exist.
        0 if no rooms of that room_type exist.
        """

        max_members_by_room_type: Dict[str, int] = {}

        for size in const.ROOM_TYPES:
            # Initialise max members for each room type to 0
            if size not in max_members_by_room_type.keys():
                max_members_by_room_type[size] = 0

            rooms = self.get_rooms()
            for room in rooms:
                room: Room
                if room.is_composite():
                    room_members = room.get_members()

                    # Can just use the first room to get size given all rooms in composite room
                    # are the same size (homogeneous)
                    room_member_type = self.get_room_by_name(room_members[0]).get_type()

                    num_room_members = len(room_members)
                else:
                    num_room_members = 1
                    room_member_type = room.get_type()

                if room_member_type != size:
                    continue

                max_members_by_room_type[size] = max(
                    max_members_by_room_type[size], num_room_members
                )

        return max_members_by_room_type

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

    def get_independence_number(self, room_type: str, room_size: int) -> int:
        """
        Gets the independence number for the given room type and room size
        """

        # base case
        if room_size == 1:
            return self.get_num_rooms_by_type_and_size(room_type, room_size)

        # find joining rooms
        rooms: List[Room] = self.get_rooms_by_size_and_num_rooms(room_type, room_size)

        visited_members = []
        ind_num = 0
        for room in rooms:
            room: Room
            room_members: List[str] = room.get_members()

            add = True
            for member in room_members:
                if member in visited_members:
                    # We have seen a room that joins to this room before. Don't add to independence number
                    add = False
                    break

            if add:
                ind_num += 1

                # Only add the members of rooms that count towards the independence number
                visited_members.extend(room_members)

        return ind_num

    def get_dummy_room(self) -> Room:
        """
        Returns dummy room
        """

        for r in self.rooms:
            if r.get_type() == const.DUMMY:
                return r
        raise Exception("No dummy room big sad")

    def get_room_joining_map(self) -> Dict[Room, List[Room]]:
        """
        Returns the joining map
        Maps rooms to a list of rooms they are joining.
        Only maps to size of room 1 larger than current size
        """

        return self.room_joining_map

    def get_num_compatible_rooms(self, room_type: str, room_size: int) -> int:
        """
        Given a room type, return the number of rooms that are compatible with an event
        that would fit into a room of room_type, room_size
        Return: int
        """

        if room_size > 1:
            return self.get_num_rooms_by_type(room_type)
        else:
            if room_type == const.SMALL:
                return (
                    len(self.get_small_rooms())
                    + len(self.get_medium_rooms())
                    + len(self.get_large_rooms())
                )
            elif room_type == const.MEDIUM:
                return len(self.get_medium_rooms()) + len(self.get_large_rooms())
            elif room_type == const.LARGE:
                return len(self.get_large_rooms())

    def get_num_rooms_by_type(self, room_type: str) -> int:
        """
        Given a room type, return the number of rooms of that type
        """

        if room_type == const.SMALL:
            return len(self.get_small_rooms())
        elif room_type == const.MEDIUM:
            return len(self.get_medium_rooms())
        elif room_type == const.LARGE:
            return len(self.get_large_rooms())
        else:
            raise Exception("Room Type not found")

    def get_num_rooms_by_type_and_size(self, room_type: str, room_size: int) -> int:
        """
        Given a room type and room size, return the number of rooms of that type and size
        """

        return len(self.get_rooms_by_size_and_num_rooms(room_type, room_size))

    def get_immediate_parent_rooms(self, room: Room) -> List[Room]:
        """
        Given a room, returns the list of Rooms that are the immediate parent rooms of the given room
        """

        return self.room_joining_map.get(room, [])

    def construct_joining_map(self) -> Dict[Room, List[Room]]:
        """
        Maps rooms to a list of rooms they are joining.
        Only maps to size of room 1 larger than current size
        """

        self.room_joining_map: Dict[Room, List[Room]] = {}

        for room_type in const.ROOM_TYPES:
            for room_size in range(1, 6 + 1 - 1):
                rooms: List[Room] = self.get_rooms_by_size_and_num_rooms(
                    room_type, room_size
                )
                for room in rooms:
                    room: Room

                    direct_parent_rooms: List[Room] = []

                    for super_room in self.get_rooms_by_size_and_num_rooms(
                        room_type, room_size + 1
                    ):
                        super_room: Room
                        if not super_room.is_composite():
                            raise Exception("Error. Composite Room Expected")

                        if room.get_room() in super_room.get_members():
                            direct_parent_rooms.append(super_room)

                    self.room_joining_map[room] = direct_parent_rooms

    def get_adjacent_rooms(self, room: Room) -> List[Room]:
        """
        Gets the joining rooms of a given room (composite)
        """

        joining_rooms: List[Room] = []

        for comp_room in self.get_composite_rooms():
            if room.get_room() in comp_room.get_members():
                joining_rooms.append(comp_room)

        return joining_rooms

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
