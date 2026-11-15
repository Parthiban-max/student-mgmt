from datetime import date
from io import BytesIO

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView

from academics.models import Course, Department, Mark, Subject
from attendance.models import Attendance
from faculty.models import Faculty
from students.models import Student


def staff_scope(queryset, user, subject_path="subject__faculty__user"):
    if not user.is_superuser and user.role == "FACULTY":
        return queryset.filter(**{subject_path: user})
    return queryset


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "reports/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        attendance = staff_scope(Attendance.objects.all(), self.request.user)
        attendance_total = attendance.count()
        present_count = attendance.filter(status=Attendance.Status.PRESENT).count()
        eligible_count = attendance.exclude(status=Attendance.Status.LEAVE).count()
        absent_today = attendance.filter(date=today, status=Attendance.Status.ABSENT).count()
        monthly = list(attendance.annotate(month=TruncMonth("date")).values("month").annotate(
            present=Count("id", filter=Q(status=Attendance.Status.PRESENT)),
            absent=Count("id", filter=Q(status=Attendance.Status.ABSENT)),
        ).order_by("-month")[:8])
        monthly.reverse()
        marks = staff_scope(Mark.objects.all(), self.request.user)
        performance = marks.values("subject__name").annotate(average=Avg("score")).order_by("subject__name")[:10]
        students = Student.objects.select_related("department", "course")
        if not (self.request.user.is_superuser or self.request.user.role == "ADMIN"):
            students = students.filter(course__subjects__faculty__user=self.request.user).distinct()
        context.update({
            "page_title": "Dashboard",
            "student_count": students.count(),
            "faculty_count": Faculty.objects.count(),
            "course_count": Course.objects.count(),
            "department_count": Department.objects.count(),
            "present_today": attendance.filter(date=today, status=Attendance.Status.PRESENT).count(),
            "absent_today": absent_today,
            "attendance_rate": round(present_count * 100 / eligible_count) if eligible_count else 0,
            "average_score": round(marks.aggregate(value=Avg("score"))["value"] or 0, 1),
            "performance_labels": [item["subject__name"] for item in performance],
            "performance_values": [float(item["average"] or 0) for item in performance],
            "recent_students": students.order_by("-created_at")[:6],
            "monthly_labels": [item["month"].strftime("%b %Y") for item in monthly if item["month"]],
            "monthly_present": [item["present"] for item in monthly if item["month"]],
            "monthly_absent": [item["absent"] for item in monthly if item["month"]],
            "department_labels": list(
                students.values("department__name").annotate(total=Count("id")).order_by("department__name")
                .values_list("department__name", flat=True)
            ),
            "department_values": list(
                students.values("department__name").annotate(total=Count("id")).order_by("department__name")
                .values_list("total", flat=True)
            ),
        })
        if not (self.request.user.is_superuser or self.request.user.role == "ADMIN"):
            context["faculty_count"] = Faculty.objects.filter(pk=self.request.user.faculty_profile.pk).count() if hasattr(self.request.user, "faculty_profile") else 0
            context["course_count"] = Subject.objects.filter(faculty__user=self.request.user).values("course_id").distinct().count()
        return context


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = "reports/index.html"
    extra_context = {"page_title": "Reports"}


class ReportExportView(LoginRequiredMixin, View):
    report_specs = {
        "students": ("Student reports", ("Student ID", "Name", "Email", "Department", "Course", "Year")),
        "attendance": ("Attendance reports", ("Date", "Student ID", "Student", "Subject", "Status")),
        "marks": ("Academic performance reports", ("Student ID", "Student", "Subject", "Semester", "Score", "Grade")),
    }

    def get_rows(self, report_type):
        if report_type == "students":
            records = Student.objects.select_related("department", "course").order_by("last_name", "first_name")
            if not self.request.user.is_superuser and self.request.user.role == "FACULTY":
                records = records.filter(course__subjects__faculty__user=self.request.user).distinct()
            return [[s.student_id, s.full_name, s.email, s.department.name, s.course.name, s.year] for s in records]
        if report_type == "attendance":
            records = staff_scope(
                Attendance.objects.select_related("student", "subject").order_by("-date"), self.request.user
            )
            return [[r.date.isoformat(), r.student.student_id, r.student.full_name, r.subject.name, r.get_status_display()] for r in records]
        if report_type == "marks":
            records = staff_scope(
                Mark.objects.select_related("student", "subject", "semester"), self.request.user
            )
            return [[m.student.student_id, m.student.full_name, m.subject.name, str(m.semester), str(m.score), m.grade] for m in records]
        return None

    def get(self, request, report_type, output_format):
        if report_type not in self.report_specs or output_format not in {"xlsx", "pdf"}:
            from django.http import Http404

            raise Http404("Report format or type not found.")
        title, headers = self.report_specs[report_type]
        rows = self.get_rows(report_type)
        if output_format == "xlsx":
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill

            workbook = Workbook()
            sheet = workbook.active
            sheet.title = title[:31]
            sheet.append(headers)
            for cell in sheet[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="243B64")
            for row in rows:
                sheet.append([
                    "'" + value if isinstance(value, str) and value.startswith(("=", "+", "-", "@")) else value
                    for value in row
                ])
            for column in sheet.columns:
                width = min(max(len(str(cell.value or "")) for cell in column) + 2, 40)
                sheet.column_dimensions[column[0].column_letter].width = width
            output = BytesIO()
            workbook.save(output)
            response = HttpResponse(
                output.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f'attachment; filename="{report_type}-report.xlsx"'
            return response

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

        output = BytesIO()
        document = SimpleDocTemplate(output, pagesize=landscape(letter), title=title)
        table = Table([headers] + [[str(cell) for cell in row] for row in rows], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243b64")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#dce3ed")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6fa")]),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        document.build([table])
        response = HttpResponse(output.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{report_type}-report.pdf"'
        return response
