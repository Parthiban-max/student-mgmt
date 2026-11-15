from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.permissions import AdminRequiredMixin, LoginRequiredMixin
from .forms import StudentForm
from .models import Student


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "shared/list.html"
    context_object_name = "students"
    paginate_by = 15
    extra_context = {"page_title": "Students", "create_url": "students:create", "create_label": "Add student"}

    def get_queryset(self):
        queryset = Student.objects.select_related("department", "course")
        user = self.request.user
        if not user.is_superuser and user.role == "FACULTY":
            queryset = queryset.filter(course__subjects__faculty__user=user).distinct()
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(student_id__icontains=search) | Q(first_name__icontains=search)
                | Q(last_name__icontains=search) | Q(email__icontains=search)
            )
        department_id = self.request.GET.get("department", "")
        if department_id.isdigit():
            queryset = queryset.filter(department_id=int(department_id))
        year = self.request.GET.get("year", "")
        if year.isdigit() and 1 <= int(year) <= 8:
            queryset = queryset.filter(year=int(year))
        return queryset

    def get_context_data(self, **kwargs):
        from academics.models import Department

        context = super().get_context_data(**kwargs)
        context.update({"departments": Department.objects.all(), "search_query": self.request.GET.get("q", "")})
        return context


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = "students/detail.html"
    context_object_name = "student"

    def get_queryset(self):
        queryset = Student.objects.select_related("department", "course").prefetch_related("attendance_records", "marks")
        user = self.request.user
        if not user.is_superuser and user.role == "FACULTY":
            queryset = queryset.filter(course__subjects__faculty__user=user).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        records = context["student"].attendance_records.exclude(status="LEAVE")
        total = records.count()
        context["attendance_rate"] = round(records.filter(status="PRESENT").count() * 100 / total) if total else 0
        return context


class StudentCreateView(AdminRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("students:list")
    extra_context = {"page_title": "Register student"}

    def form_valid(self, form):
        messages.success(self.request, "Student record created.")
        return super().form_valid(form)


class StudentUpdateView(AdminRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("students:list")
    extra_context = {"page_title": "Edit student"}


class StudentDeleteView(AdminRequiredMixin, DeleteView):
    model = Student
    template_name = "shared/confirm_delete.html"
    success_url = reverse_lazy("students:list")
