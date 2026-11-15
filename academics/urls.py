from django.urls import path

from .views import (
    CourseCreateView, CourseDeleteView, CourseListView, CourseUpdateView,
    DepartmentCreateView, DepartmentDeleteView, DepartmentListView, DepartmentUpdateView,
    MarkCreateView, MarkDeleteView, MarkListView, MarkUpdateView,
    SemesterCreateView, SemesterDeleteView, SemesterListView, SemesterUpdateView,
    SubjectCreateView, SubjectDeleteView, SubjectListView, SubjectUpdateView,
)

app_name = "academics"
urlpatterns = [
    path("departments/", DepartmentListView.as_view(), name="departments"),
    path("departments/new/", DepartmentCreateView.as_view(), name="department_create"),
    path("departments/<int:pk>/edit/", DepartmentUpdateView.as_view(), name="department_edit"),
    path("departments/<int:pk>/delete/", DepartmentDeleteView.as_view(), name="department_delete"),
    path("courses/", CourseListView.as_view(), name="courses"),
    path("courses/new/", CourseCreateView.as_view(), name="course_create"),
    path("courses/<int:pk>/edit/", CourseUpdateView.as_view(), name="course_edit"),
    path("courses/<int:pk>/delete/", CourseDeleteView.as_view(), name="course_delete"),
    path("semesters/", SemesterListView.as_view(), name="semesters"),
    path("semesters/new/", SemesterCreateView.as_view(), name="semester_create"),
    path("semesters/<int:pk>/edit/", SemesterUpdateView.as_view(), name="semester_edit"),
    path("semesters/<int:pk>/delete/", SemesterDeleteView.as_view(), name="semester_delete"),
    path("subjects/", SubjectListView.as_view(), name="subjects"),
    path("subjects/new/", SubjectCreateView.as_view(), name="subject_create"),
    path("subjects/<int:pk>/edit/", SubjectUpdateView.as_view(), name="subject_edit"),
    path("subjects/<int:pk>/delete/", SubjectDeleteView.as_view(), name="subject_delete"),
    path("marks/", MarkListView.as_view(), name="marks"),
    path("marks/new/", MarkCreateView.as_view(), name="mark_create"),
    path("marks/<int:pk>/edit/", MarkUpdateView.as_view(), name="mark_edit"),
    path("marks/<int:pk>/delete/", MarkDeleteView.as_view(), name="mark_delete"),
]
