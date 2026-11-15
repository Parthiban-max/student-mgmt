from django.conf import settings
from django.db import models


class Faculty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="faculty_profile")
    faculty_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey("academics.Department", on_delete=models.PROTECT, related_name="faculty")
    phone = models.CharField(max_length=20, blank=True)
    designation = models.CharField(max_length=100, default="Lecturer")
    joined_on = models.DateField()

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    def __str__(self):
        return f"{self.faculty_id} - {self.full_name}"
