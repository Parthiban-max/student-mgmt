from django.contrib import admin

from .models import Course, Department, Mark, Semester, Subject

admin.site.register([Course, Department, Mark, Semester, Subject])
