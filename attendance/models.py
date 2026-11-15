from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        LEAVE = "LEAVE", "Leave"

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="attendance_records")
    subject = models.ForeignKey("academics.Subject", on_delete=models.PROTECT, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=8, choices=Status.choices)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="marked_attendance")
    remarks = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "student__last_name"]
        constraints = [
            models.UniqueConstraint(fields=["student", "subject", "date"], name="unique_student_subject_attendance_day")
        ]

    def clean(self):
        if self.student_id and self.subject_id and self.student.course_id != self.subject.course_id:
            raise ValidationError({"subject": "The subject must belong to the student's course."})

    def __str__(self):
        return f"{self.student.student_id} • {self.date} • {self.get_status_display()}"
