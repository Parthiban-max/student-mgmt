from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from academics.models import Course, Department, Mark, Semester, Subject
from faculty.models import Faculty
from students.models import Student


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class AcademicRecordTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Engineering", code="ENG")
        self.course = Course.objects.create(department=self.department, name="Engineering", code="BE-ENG")
        self.semester = Semester.objects.create(course=self.course, number=1, academic_year="2026-2027")
        user = get_user_model().objects.create_user("teacher", password="Strong-test-password-42")
        faculty = Faculty.objects.create(user=user, faculty_id="FAC-ENG", department=self.department, joined_on="2025-01-01")
        self.subject = Subject.objects.create(course=self.course, semester=self.semester, name="Math", code="MTH-1", faculty=faculty)
        self.student = Student.objects.create(
            first_name="Alan", last_name="Turing", email="alan@example.com", department=self.department,
            course=self.course, year=1, enrolled_on="2026-08-01",
        )

    def test_grade_thresholds(self):
        mark = Mark(student=self.student, subject=self.subject, semester=self.semester, score=92)
        self.assertEqual(mark.grade, "A+")
        mark.score = 69
        self.assertEqual(mark.grade, "C")
        mark.score = 49
        self.assertEqual(mark.grade, "F")

    def test_subject_list_is_login_protected(self):
        response = self.client.get(reverse("academics:subjects"))
        self.assertEqual(response.status_code, 302)

    def test_faculty_only_sees_assigned_subjects(self):
        user = self.subject.faculty.user
        self.client.force_login(user)
        response = self.client.get(reverse("academics:subjects"))
        self.assertContains(response, "MTH-1")

    def test_mark_validation_rejects_another_course_student(self):
        other_department = Department.objects.create(name="Arts", code="ART")
        other_course = Course.objects.create(department=other_department, name="Fine Arts", code="BA-ART")
        other_student = Student.objects.create(
            first_name="Maya", last_name="Angelou", email="maya@example.com", department=other_department,
            course=other_course, year=1, enrolled_on="2026-08-01",
        )
        mark = Mark(student=other_student, subject=self.subject, semester=self.semester, score=85)
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            mark.full_clean()
