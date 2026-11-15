from django.urls import path

from .views import ReportExportView, ReportsView

app_name = "reports"
urlpatterns = [
    path("", ReportsView.as_view(), name="index"),
    path("export/<str:report_type>/<str:output_format>/", ReportExportView.as_view(), name="export"),
]
