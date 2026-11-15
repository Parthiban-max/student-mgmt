from django.contrib import messages
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.permissions import AdminRequiredMixin, LoginRequiredMixin, StaffRequiredMixin
from .forms import CourseForm, DepartmentForm, MarkForm, SemesterForm, SubjectForm
from .models import Course, Department, Mark, Semester, Subject


class ResourceListView(LoginRequiredMixin, ListView):
    template_name = "shared/resource_list.html"
    paginate_by = 15
    title = ""
    fields = ()
    create_url = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        objects = context["object_list"]
        context.update({
            "page_title": self.title,
            "columns": [label for label, _ in self.fields],
            "rows": [
                {"id": obj.pk, "values": [str(getattr(obj, attr)) for _, attr in self.fields]}
                for obj in objects
            ],
            "create_url": self.create_url,
            "app_name": self.request.resolver_match.namespace,
        })
        return context


class DepartmentListView(ResourceListView):
    model = Department
    title = "Departments"
    queryset = Department.objects.annotate(course_total=Count("courses"))
    fields = (("Code", "code"), ("Department", "name"), ("Courses", "course_total"))
    create_url = "academics:department_create"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"edit_route": "academics:department_edit", "delete_route": "academics:department_delete"})
        return context


class CourseListView(ResourceListView):
    model = Course
    queryset = Course.objects.select_related("department")
    title = "Courses"
    fields = (("Code", "code"), ("Course", "name"), ("Department", "department"), ("Duration", "duration_years"))
    create_url = "academics:course_create"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"edit_route": "academics:course_edit", "delete_route": "academics:course_delete"})
        return context


class SemesterListView(ResourceListView):
    model = Semester
    queryset = Semester.objects.select_related("course")
    title = "Semesters"
    fields = (("Course", "course"), ("Semester", "number"), ("Academic year", "academic_year"))
    create_url = "academics:semester_create"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"edit_route": "academics:semester_edit", "delete_route": "academics:semester_delete"})
        return context


class SubjectListView(ResourceListView):
    model = Subject
    queryset = Subject.objects.select_related("course", "semester", "faculty__user")
    title = "Subjects"
    fields = (("Code", "code"), ("Subject", "name"), ("Course", "course"), ("Semester", "semester"), ("Faculty", "faculty"))
    create_url = "academics:subject_create"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_superuser and user.role == "FACULTY":
            return queryset.filter(faculty__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser or self.request.user.role == "ADMIN":
            context.update({"edit_route": "academics:subject_edit", "delete_route": "academics:subject_delete"})
        return context


class MarkListView(ResourceListView):
    model = Mark
    queryset = Mark.objects.select_related("student", "subject", "semester")
    title = "Marks & results"
    fields = (("Student", "student"), ("Subject", "subject"), ("Semester", "semester"), ("Score", "score"), ("Grade", "grade"))
    create_url = "academics:mark_create"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_superuser and user.role == "FACULTY":
            queryset = queryset.filter(subject__faculty__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser or self.request.user.role == "ADMIN":
            context.update({"edit_route": "academics:mark_edit", "delete_route": "academics:mark_delete"})
        return context


class AdminResourceMixin:
    def form_valid(self, form):
        messages.success(self.request, "Changes saved.")
        return super().form_valid(form)


class DepartmentCreateView(AdminResourceMixin, AdminRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("academics:departments")
    extra_context = {"page_title": "Add department"}


class DepartmentUpdateView(AdminResourceMixin, AdminRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("academics:departments")
    extra_context = {"page_title": "Edit department"}


class CourseCreateView(AdminResourceMixin, AdminRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("academics:courses")
    extra_context = {"page_title": "Add course"}


class CourseUpdateView(AdminResourceMixin, AdminRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("academics:courses")
    extra_context = {"page_title": "Edit course"}


class SemesterCreateView(AdminResourceMixin, AdminRequiredMixin, CreateView):
    model = Semester
    form_class = SemesterForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("academics:semesters")
    extra_context = {"page_title": "Add semester"}


class SemesterUpdateView(AdminResourceMixin, AdminRequiredMixin, UpdateView):
    model = Semester
    form_class = SemesterForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("academics:semesters")
    extra_context = {"page_title": "Edit semester"}


class SubjectCreateView(AdminResourceMixin, AdminRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("academics:subjects")
    extra_context = {"page_title": "Add subject"}


class SubjectUpdateView(AdminResourceMixin, AdminRequiredMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("academics:subjects")
    extra_context = {"page_title": "Edit subject"}


class MarkFormMixin:
    form_class = MarkForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if not user.is_superuser and user.role == "FACULTY":
            form.fields["subject"].queryset = Subject.objects.filter(faculty__user=user)
        if self.request.method == "POST":
            subject_id = self.request.POST.get("subject")
            if subject_id:
                form.fields["student"].queryset = form.fields["student"].queryset.filter(course__subjects__id=subject_id).distinct()
                form.fields["semester"].queryset = form.fields["semester"].queryset.filter(subjects__id=subject_id).distinct()
        return form

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        return super().form_valid(form)


class MarkCreateView(MarkFormMixin, AdminResourceMixin, StaffRequiredMixin, CreateView):
    model = Mark
    template_name = "shared/form.html"
    success_url = reverse_lazy("academics:marks")
    extra_context = {"page_title": "Enter marks"}


class MarkUpdateView(MarkFormMixin, AdminResourceMixin, StaffRequiredMixin, UpdateView):
    model = Mark
    template_name = "shared/form.html"
    success_url = reverse_lazy("academics:marks")
    extra_context = {"page_title": "Update marks"}

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_superuser and user.role == "FACULTY":
            queryset = queryset.filter(subject__faculty__user=user)
        return queryset


class AdminDeleteView(AdminRequiredMixin, DeleteView):
    template_name = "shared/confirm_delete.html"

    def form_valid(self, form):
        from django.db.models.deletion import ProtectedError
        from django.http import HttpResponseRedirect

        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, "This record is still in use and cannot be deleted. Update or remove its related records first.")
            return HttpResponseRedirect(self.get_success_url())
        messages.success(self.request, "Record deleted.")
        return HttpResponseRedirect(self.get_success_url())


class DepartmentDeleteView(AdminDeleteView):
    model = Department
    success_url = reverse_lazy("academics:departments")


class CourseDeleteView(AdminDeleteView):
    model = Course
    success_url = reverse_lazy("academics:courses")


class SemesterDeleteView(AdminDeleteView):
    model = Semester
    success_url = reverse_lazy("academics:semesters")


class SubjectDeleteView(AdminDeleteView):
    model = Subject
    success_url = reverse_lazy("academics:subjects")


class MarkDeleteView(AdminDeleteView):
    model = Mark
    success_url = reverse_lazy("academics:marks")
