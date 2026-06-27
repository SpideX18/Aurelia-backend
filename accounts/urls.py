from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ActivityLogListView,
    ChangePasswordView,
    CustomerListView,
    CustomTokenObtainPairView,
    ForgotPasswordView,
    LogoutView,
    MeView,
    RegisterView,
    ResetPasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("customers/", CustomerListView.as_view(), name="customers"),
    path("activity-logs/", ActivityLogListView.as_view(), name="activity-logs"),
]
