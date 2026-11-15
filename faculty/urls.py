from django.urls import path

from .views import FacultyCreateView, FacultyDeleteView, FacultyListView, FacultyUpdateView

app_name = "faculty"
urlpatterns = [
    path("", FacultyListView.as_view(), name="list"),
    path("new/", FacultyCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", FacultyUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", FacultyDeleteView.as_view(), name="delete"),
]
