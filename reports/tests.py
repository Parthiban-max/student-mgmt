from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from academics.models import Course, Department
from students.models import Student


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class DashboardAndExportTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            "admin", "admin@example.com", "A-strong-admin-password-2026"
        )
        department = Department.objects.create(name="Design", code="DSN")
        course = Course.objects.create(department=department, name="Design Studies", code="BA-DSN")
        Student.objects.create(
            first_name="Jordan", last_name="Lee", email="jordan@example.com",
            department=department, course=course, year=1, enrolled_on="2026-08-01",
        )
        self.client.force_login(self.admin)

    def test_dashboard_renders_aggregated_metrics(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total students")
        self.assertContains(response, "Jordan Lee")

    def test_student_excel_export_is_a_download(self):
        response = self.client.get(reverse("reports:export", args=["students", "xlsx"]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("spreadsheetml", response["Content-Type"])
        self.assertIn("attachment;", response["Content-Disposition"])

    def test_student_pdf_export_is_a_download(self):
        response = self.client.get(reverse("reports:export", args=["students", "pdf"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_unknown_report_format_returns_not_found(self):
        response = self.client.get(reverse("reports:export", args=["students", "csv"]))
        self.assertEqual(response.status_code, 404)
