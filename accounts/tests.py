from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from academics.models import Course, Department, Semester, Subject
from faculty.models import Faculty
from students.models import Student

User = get_user_model()


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class RoleAccessTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Computing", code="CSE")
        self.course = Course.objects.create(department=self.department, name="Computer Science", code="BSC-CS", duration_years=4)
        self.semester = Semester.objects.create(course=self.course, number=1, academic_year="2026-2027")
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "Strong-test-password-42")
        self.faculty_user = User.objects.create_user(
            "lecturer", "lecturer@example.com", "Strong-test-password-42", role=User.Role.FACULTY,
            first_name="Ada", last_name="Lovelace",
        )
        self.faculty = Faculty.objects.create(
            user=self.faculty_user, faculty_id="FAC-001", department=self.department, joined_on="2024-01-01"
        )
        self.subject = Subject.objects.create(
            course=self.course, semester=self.semester, name="Algorithms", code="CS101", faculty=self.faculty
        )
        self.student = Student.objects.create(
            first_name="Grace", last_name="Hopper", email="grace@example.com",
            department=self.department, course=self.course, year=1, enrolled_on="2026-08-01",
        )

    def test_student_identifier_is_generated(self):
        self.assertRegex(self.student.student_id, r"^STU-[A-F0-9]{10}$")

    def test_faculty_cannot_open_student_mutation_form(self):
        self.client.force_login(self.faculty_user)
        response = self.client.get(reverse("students:create"))
        self.assertEqual(response.status_code, 403)

    def test_faculty_can_view_assigned_course_student(self):
        self.client.force_login(self.faculty_user)
        response = self.client.get(reverse("students:detail", args=[self.student.pk]))
        self.assertEqual(response.status_code, 200)

    def test_faculty_cannot_view_unassigned_course_student(self):
        other_department = Department.objects.create(name="Science", code="SCI")
        other_course = Course.objects.create(department=other_department, name="Physics", code="BSC-PHY")
        other_student = Student.objects.create(
            first_name="Katherine", last_name="Johnson", email="kj@example.com",
            department=other_department, course=other_course, year=1, enrolled_on="2026-08-01",
        )
        self.client.force_login(self.faculty_user)
        response = self.client.get(reverse("students:detail", args=[other_student.pk]))
        self.assertEqual(response.status_code, 404)

    def test_login_page_is_available(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
