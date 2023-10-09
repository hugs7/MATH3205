from typing import List


class Curriculum:
    def __init__(self, curriculum_data):
        self.name = curriculum_data.get("Curriculum")
        self.primary_course_names = curriculum_data.get("PrimaryCourses", [])
        self.secondary_course_names = curriculum_data.get("SecondaryCourses", [])

    def __repr__(self):
        # TODO fix to simplify
        return f"Curriculum: {self.name}\nPrimary Courses: {', '.join(self.primary_course_names)}\nSecondary Courses: {', '.join(self.secondary_course_names)}"

    def get_course_names(self) -> List[str]:
        """
        Returns the list of primary and secondary course names as a list of strings
        """

        return self.primary_course_names + self.secondary_course_names

    def get_primary_course_names(self) -> List[str]:
        """
        Returns list of primary courses as list of strings
        """

        return self.primary_course_names

    def get_secondary_course_names(self) -> List[str]:
        """
        Returns list of secondary courses as list of strings
        """

        return self.secondary_course_names


class CurriculaManager:
    def __init__(self):
        self.curricula: List[Curriculum] = []

    def add_curriculum(self, curriculum_data) -> Curriculum:
        """
        Creates Curriculum and adds it to the CurriculaManager
        Returns new curriculum
        """

        new_curriculum = Curriculum(curriculum_data)
        self.curricula.append(new_curriculum)

        return new_curriculum

    def get_curricula(self) -> List[Curriculum]:
        """
        Returns curricula as list of Curriculum
        """

        return self.curricula

    def get_curricula_by_name(self, course_name: str) -> Curriculum:
        """
        Finds course by name and returns course instance
        Raises a CourseNotFoundException if the course is not managed by
        this CourseManager
        """
        curricula_list = []
        for curricula in self.curricula:
            if course_name in curricula.get_course_names():
                curricula_list.append(curricula)

        return curricula_list

    def __str__(self):
        return "\n\n".join([str(curriculum) for curriculum in self.curricula])
