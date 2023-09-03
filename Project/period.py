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

    def __lt__(self, other_period) -> bool:
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

    def __gt__(self, other_period) -> bool:
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
