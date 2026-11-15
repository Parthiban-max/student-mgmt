from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from academics.models import Course, Department, Semester, Subject
from attendance.forms import AttendanceForm
from attendance.models import Attendance
from faculty.models import Faculty
from students.models import Student


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class AttendanceWorkflowTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Business", code="BUS")
        self.course = Course.objects.create(department=self.department, name="Commerce", code="B-COM")
        self.semester = Semester.objects.create(course=self.course, number=1, academic_year="2026-2027")
        self.user = get_user_model().objects.create_user("faculty", password="Strong-test-password-42")
        self.faculty = Faculty.objects.create(user=self.user, faculty_id="FAC-BUS", department=self.department, joined_on="2025-01-01")
        self.subject = Subject.objects.create(course=self.course, semester=self.semester, name="Accounting", code="ACC-1", faculty=self.faculty)
        self.student = Student.objects.create(
            first_name="Rita", last_name="Patel", email="rita@example.com", department=self.department,
            course=self.course, year=1, enrolled_on="2026-08-01",
        )

    def test_faculty_attendance_form_only_offers_assigned_subject(self):
        form = AttendanceForm(user=self.user)
        self.assertEqual(list(form.fields["subject"].queryset), [self.subject])

    def test_duplicate_daily_attendance_is_rejected(self):
        Attendance.objects.create(student=self.student, subject=self.subject, date="2026-09-01", status=Attendance.Status.PRESENT)
        duplicate = Attendance(student=self.student, subject=self.subject, date="2026-09-01", status=Attendance.Status.ABSENT)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_analytics_requires_login(self):
        response = self.client.get(reverse("attendance:analytics"))
        self.assertEqual(response.status_code, 302)

    def test_attendance_creation_page_available_to_faculty(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("attendance:create"))
        self.assertEqual(response.status_code, 200)
