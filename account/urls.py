from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import SignUpView

app_name = "account"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="account/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", SignUpView.as_view(), name="register"),
]
