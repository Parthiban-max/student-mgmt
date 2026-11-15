from django.contrib.auth import views as auth_views
from django.urls import path

from .views import SignInView, UpdatePasswordView

app_name = "accounts"
urlpatterns = [
    path("login/", SignInView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password/", UpdatePasswordView.as_view(), name="password"),
]
