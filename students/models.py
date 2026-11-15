import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Student(models.Model):
    class Gender(models.TextChoices):
        FEMALE = "F", "Female"
        MALE = "M", "Male"
        OTHER = "O", "Other"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="student_profile")
    student_id = models.CharField(max_length=24, unique=True, editable=False)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    department = models.ForeignKey("academics.Department", on_delete=models.PROTECT, related_name="students")
    course = models.ForeignKey("academics.Course", on_delete=models.PROTECT, related_name="students")
    year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    enrolled_on = models.DateField()
    address = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=120, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.department_id and self.course_id and self.course.department_id != self.department_id:
            raise ValidationError({"course": "The selected course must belong to the selected department."})
        if self.course_id and self.year and self.year > self.course.duration_years:
            raise ValidationError({"year": "The student year cannot exceed the course duration."})

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = f"STU-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"
