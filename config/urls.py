from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("students/", include("students.urls")),
    path("faculty/", include("faculty.urls")),
    path("academics/", include("academics.urls")),
    path("attendance/", include("attendance.urls")),
    path("reports/", include("reports.urls")),
    path("", include("reports.dashboard_urls")),
]
