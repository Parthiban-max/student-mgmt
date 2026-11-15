from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=12, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def course_count(self):
        return self.courses.count()


class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="courses")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=16, unique=True)
    duration_years = models.PositiveSmallIntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(8)])

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Semester(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="semesters")
    number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(16)])
    academic_year = models.CharField(max_length=9, help_text="For example, 2026-2027")
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-academic_year", "number"]
        constraints = [
            models.UniqueConstraint(fields=["course", "number", "academic_year"], name="unique_course_semester_year")
        ]

    def __str__(self):
        return f"{self.course.code} • Semester {self.number} ({self.academic_year})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            raise ValidationError({"ends_on": "The end date must be on or after the start date."})


class Subject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="subjects")
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name="subjects")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=16, unique=True)
    credits = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(12)])
    faculty = models.ForeignKey(
        "faculty.Faculty", on_delete=models.SET_NULL, related_name="subjects", null=True, blank=True
    )

    class Meta:
        ordering = ["course__name", "semester__number", "name"]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.semester_id and self.course_id and self.semester.course_id != self.course_id:
            raise ValidationError({"semester": "The selected semester must belong to the selected course."})
        if self.faculty_id and self.course_id and self.faculty.department_id != self.course.department_id:
            raise ValidationError({"faculty": "The faculty member must belong to the course's department."})

    def __str__(self):
        return f"{self.code} - {self.name}"


class Mark(models.Model):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="marks")
    subject = models.ForeignKey("academics.Subject", on_delete=models.PROTECT, related_name="marks")
    semester = models.ForeignKey("academics.Semester", on_delete=models.PROTECT, related_name="marks")
    score = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    recorded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="recorded_marks")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["student__last_name", "subject__name"]
        constraints = [
            models.UniqueConstraint(fields=["student", "subject", "semester"], name="unique_student_subject_semester_mark")
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.subject_id and self.semester_id and self.subject.semester_id != self.semester_id:
            raise ValidationError({"semester": "The semester must match the subject's semester."})
        if self.student_id and self.subject_id and self.student.course_id != self.subject.course_id:
            raise ValidationError({"subject": "The subject must belong to the student's course."})

    @property
    def grade(self):
        if self.score >= 90:
            return "A+"
        if self.score >= 80:
            return "A"
        if self.score >= 70:
            return "B"
        if self.score >= 60:
            return "C"
        if self.score >= 50:
            return "D"
        return "F"
