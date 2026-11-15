from django.urls import path

from .views import (
    AttendanceAnalyticsView, AttendanceCreateView, AttendanceDeleteView, AttendanceHistoryView,
    AttendanceListView, AttendanceUpdateView,
)

app_name = "attendance"
urlpatterns = [
    path("", AttendanceListView.as_view(), name="list"),
    path("new/", AttendanceCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", AttendanceUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", AttendanceDeleteView.as_view(), name="delete"),
    path("analytics/", AttendanceAnalyticsView.as_view(), name="analytics"),
    path("student/<int:student_id>/", AttendanceHistoryView.as_view(), name="history"),
]
