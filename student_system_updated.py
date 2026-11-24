"""
Student class diagram -> Python

UML                          Python mapping
---------------------------  ------------------------------------------
Person <<abstract>>          ABC + @abstractmethod
Student, Teacher (extends)   inheritance
- private attributes         _underscore + @property (read-only)
Student 1..* --- Course      association class: Enrollment (with grade)
Department <>--- Course      aggregation: Department holds Courses
Teacher 1 --- 0..* Course    association: course.teacher
"""
from __future__ import annotations

from abc import ABC, abstractmethod

GRADE_POINTS = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}


class Person(ABC):
    def __init__(self, name: str, email: str):
        self._name = name
        self._email = email

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    @abstractmethod
    def get_role(self) -> str: ...

    def __str__(self) -> str:
        return f"{self.get_role()}: {self._name}"


class Student(Person):
    def __init__(self, name: str, email: str, student_id: str):
        super().__init__(name, email)
        self._student_id = student_id
        self._enrollments: list[Enrollment] = []

    @property
    def student_id(self) -> str:
        return self._student_id

    @property
    def enrollments(self) -> list[Enrollment]:
        return list(self._enrollments)

    def get_role(self) -> str:
        return "Student"

    def enroll(self, course: Course) -> Enrollment:
        if any(e.course is course for e in self._enrollments):
            raise ValueError(f"{self._name} is already enrolled in {course.code}")
        enrollment = Enrollment(self, course)
        self._enrollments.append(enrollment)
        course._add_enrollment(enrollment)
        return enrollment

    def calculate_gpa(self) -> float:
        graded = [e for e in self._enrollments if e.grade]
        credits = sum(e.course.credits for e in graded)
        if credits == 0:
            return 0.0
        points = sum(GRADE_POINTS[e.grade] * e.course.credits for e in graded)
        return round(points / credits, 2)


class Teacher(Person):
    def __init__(self, name: str, email: str, employee_id: str):
        super().__init__(name, email)
        self._employee_id = employee_id
        self._courses: list[Course] = []

    def get_role(self) -> str:
        return "Teacher"

    def assign(self, course: Course) -> None:
        course.teacher = self
        self._courses.append(course)


class Course:
    def __init__(self, code: str, title: str, credits: int):
        self.code = code
        self.title = title
        self.credits = credits
        self.teacher: Teacher | None = None
        self._enrollments: list[Enrollment] = []

    def _add_enrollment(self, enrollment: Enrollment) -> None:
        self._enrollments.append(enrollment)

    @property
    def students(self) -> list[Student]:
        return [e.student for e in self._enrollments]

    def __str__(self) -> str:
        return f"{self.code} - {self.title} ({self.credits} cr)"


class Enrollment:
    """Association class between Student and Course."""

    def __init__(self, student: Student, course: Course):
        self.student = student
        self.course = course
        self._grade: str | None = None

    @property
    def grade(self) -> str | None:
        return self._grade

    def set_grade(self, grade: str) -> None:
        if grade not in GRADE_POINTS:
            raise ValueError(f"Invalid grade: {grade}")
        self._grade = grade


class Department:
    """Aggregation: courses/students can exist independently of it."""

    def __init__(self, name: str):
        self.name = name
        self.courses: list[Course] = []
        self.students: list[Student] = []

    def add_course(self, course: Course) -> None:
        self.courses.append(course)

    def add_student(self, student: Student) -> None:
        self.students.append(student)


if __name__ == "__main__":
    dept = Department("Software Engineering")
    prog = Course("SE101", "Programming", 4)
    logic = Course("CE102", "Digital Logic", 3)
    for c in (prog, logic):
        dept.add_course(c)

    teacher = Teacher("Dr. Priscilla", "priscilla@neu.edu.tr", "T001")
    teacher.assign(prog)

    s = Student("Momin", "momin@stu.edu.tr", "20245440")
    dept.add_student(s)
    s.enroll(prog).set_grade("A")
    s.enroll(logic).set_grade("B")

    print(s, "| GPA:", s.calculate_gpa())
    print(prog, "| taught by", prog.teacher, "| students:", [x.name for x in prog.students])
