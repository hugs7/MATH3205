class Curricula:
    def __init__(self, curriculum_data):
        self.curriculum = curriculum_data.get("Curriculum")
        self.primary_courses = curriculum_data.get("PrimaryCourses", [])
        self.secondary_courses = curriculum_data.get("SecondaryCourses", [])

    def __repr__(self):
        return f"Curriculum: {self.curriculum}\nPrimary Courses: {', '.join(self.primary_courses)}\nSecondary Courses: {', '.join(self.secondary_courses)}"

class CurriculaManager:
    def __init__(self):
        self.curricula = []

    def add_curriculum(self, curriculum_data):
        new_curriculum = Curricula(curriculum_data)
        self.curricula.append(new_curriculum)

    def __str__(self):
        return "\n\n".join([str(curriculum) for curriculum in self.curricula])