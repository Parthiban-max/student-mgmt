from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        FACULTY = "FACULTY", "Faculty"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.FACULTY)

    @property
    def is_admin_role(self):
        return self.is_superuser or self.role == self.Role.ADMIN

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)
