from django.contrib import messages
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.permissions import LoginRequiredMixin, StaffRequiredMixin
from academics.models import Subject
from .forms import AttendanceForm
from .models import Attendance


class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = "attendance/list.html"
    context_object_name = "records"
    paginate_by = 20

    def get_queryset(self):
        queryset = Attendance.objects.select_related("student", "subject", "subject__course")
        user = self.request.user
        if not user.is_superuser and user.role == "FACULTY":
            queryset = queryset.filter(subject__faculty__user=user)
        if self.request.GET.get("date"):
            queryset = queryset.filter(date=self.request.GET["date"])
        subject_id = self.request.GET.get("subject", "")
        if subject_id.isdigit():
            queryset = queryset.filter(subject_id=int(subject_id))
        student_id = self.request.GET.get("student", "")
        if student_id.isdigit():
            queryset = queryset.filter(student_id=int(student_id))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subjects = Subject.objects.all()
        if not self.request.user.is_superuser and self.request.user.role == "FACULTY":
            subjects = subjects.filter(faculty__user=self.request.user)
        context.update({"subjects": subjects, "page_title": "Attendance"})
        return context


class AttendanceCreateView(StaffRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("attendance:list")
    extra_context = {"page_title": "Record attendance"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.marked_by = self.request.user
        messages.success(self.request, "Attendance saved.")
        return super().form_valid(form)


class AttendanceUpdateView(StaffRequiredMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("attendance:list")
    extra_context = {"page_title": "Update attendance"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser and self.request.user.role == "FACULTY":
            queryset = queryset.filter(subject__faculty__user=self.request.user)
        return queryset

    def form_valid(self, form):
        messages.success(self.request, "Attendance updated.")
        return super().form_valid(form)


class AttendanceDeleteView(StaffRequiredMixin, DeleteView):
    model = Attendance
    template_name = "shared/confirm_delete.html"
    success_url = reverse_lazy("attendance:list")

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser and self.request.user.role == "FACULTY":
            queryset = queryset.filter(subject__faculty__user=self.request.user)
        return queryset


class AttendanceHistoryView(AttendanceListView):
    template_name = "attendance/history.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(student_id=self.kwargs["student_id"])


class AttendanceAnalyticsView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = "attendance/analytics.html"

    def get_queryset(self):
        queryset = Attendance.objects.all()
        user = self.request.user
        if not user.is_superuser and user.role == "FACULTY":
            queryset = queryset.filter(subject__faculty__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        from django.db.models.functions import TruncMonth

        context = super().get_context_data(**kwargs)
        records = self.get_queryset()
        monthly = records.annotate(month=TruncMonth("date")).values("month").annotate(
            present=Count("id", filter=Q(status=Attendance.Status.PRESENT)),
            absent=Count("id", filter=Q(status=Attendance.Status.ABSENT)),
            leave=Count("id", filter=Q(status=Attendance.Status.LEAVE)),
        ).order_by("month")
        context.update({
            "page_title": "Attendance analytics",
            "monthly_labels": [item["month"].strftime("%b %Y") for item in monthly if item["month"]],
            "monthly_present": [item["present"] for item in monthly if item["month"]],
            "monthly_absent": [item["absent"] for item in monthly if item["month"]],
            "monthly_leave": [item["leave"] for item in monthly if item["month"]],
        })
        return context
