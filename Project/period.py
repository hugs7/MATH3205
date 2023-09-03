"""
Period Class
Stores day and timeslot combination
Various methods exist on class to ease code

Hugo Burton
3/9/2023
"""


class Period:
    def __init__(self, day: int, timeslot: int) -> None:
        self.day: int = day
        self.timeslot: int = timeslot

    def get_day(self) -> int:
        """
        Returns the day number of the period
        """

        return self.day

    def get_timeslot(self) -> int:
        """
        Returns the timeslot number of the period
        """

        return self.timeslot

    def __eq__(self, other_period: "Period") -> bool:
        """
        Determines if this period is equal to another period.
        Returns True if the periods are equal, False otherwise.
        """
        if isinstance(other_period, Period):
            return (
                self.day == other_period.day and self.timeslot == other_period.timeslot
            )
        return False

    def __lt__(self, other_period: "Period") -> bool:
        """
        Determines if this period comes before another period.
        Returns True if this period is less than the other, False otherwise.
        """
        if self.day < other_period.day:
            return True
        elif self.day == other_period.day and self.timeslot < other_period.timeslot:
            return True
        else:
            return False

    def __gt__(self, other_period: "Period") -> bool:
        """
        Determines if this period comes after another period.
        Returns True if this period is greater than the other, False otherwise.
        """
        if self.day > other_period.day:
            return True
        elif self.day == other_period.day and self.timeslot > other_period.timeslot:
            return True
        else:
            return False

    def __repr__(self) -> str:
        """Repr method for period"""

        return f"({self.day}, {self.timeslot})"

    def __hash__(self):
        """
        Hash function for Period objects.
        """
        return hash((self.day, self.timeslot))

    def get_ordinal_value(self, slots_per_day: int) -> int:
        """
        Returns period number as in the data. Day * Slots per day + timeslot
        """

        return self.day * slots_per_day + self.timeslot

    @staticmethod
    def from_period_number(period_number: int, slots_per_day: int) -> "Period":
        """
        Static method to create a Period object from a period number and slots per day.
        Args:
            period_number (int): The period number.
            slots_per_day (int): The number of slots per day.
        Returns:
            Period: The Period object corresponding to the period number.
        """
        day = (period_number - 1) // slots_per_day
        timeslot = (period_number - 1) % slots_per_day

        return Period(day, timeslot)
