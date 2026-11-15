from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy

from .forms import StyledAuthenticationForm, StyledPasswordChangeForm
from .permissions import LoginRequiredMixin


class SignInView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = StyledAuthenticationForm


class UpdatePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = "shared/form.html"
    form_class = StyledPasswordChangeForm
    success_url = reverse_lazy("dashboard")
    extra_context = {"page_title": "Change password"}
