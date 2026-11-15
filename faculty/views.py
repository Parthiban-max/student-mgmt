from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.permissions import AdminRequiredMixin, LoginRequiredMixin
from .forms import FacultyForm, FacultyUpdateForm
from .models import Faculty


class FacultyListView(LoginRequiredMixin, ListView):
    model = Faculty
    template_name = "faculty/list.html"
    context_object_name = "faculty_members"
    paginate_by = 15
    extra_context = {"page_title": "Faculty", "create_url": "faculty:create", "create_label": "Add faculty"}

    def get_queryset(self):
        queryset = Faculty.objects.select_related("user", "department")
        if not self.request.user.is_superuser and self.request.user.role == "FACULTY":
            queryset = queryset.filter(user=self.request.user)
        return queryset.distinct()


class FacultyCreateView(AdminRequiredMixin, CreateView):
    form_class = FacultyForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("faculty:list")
    extra_context = {"page_title": "Add faculty"}

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Faculty account created. Share its temporary password securely.")
        return super().form_valid(form)


class FacultyUpdateView(AdminRequiredMixin, UpdateView):
    model = Faculty
    form_class = FacultyUpdateForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("faculty:list")
    extra_context = {"page_title": "Update faculty"}


class FacultyDeleteView(AdminRequiredMixin, DeleteView):
    model = Faculty
    template_name = "shared/confirm_delete.html"
    success_url = reverse_lazy("faculty:list")

    def delete(self, request, *args, **kwargs):
        from django.http import HttpResponseRedirect

        self.object = self.get_object()
        self.object.user.delete()
        messages.success(request, "Faculty profile and login account deleted.")
        return HttpResponseRedirect(self.get_success_url())
