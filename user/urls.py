from django.urls import path
from user.views import (
    CreateUserView,
    CreateTokenView,
    ManageUserView,
    PasswordResetRequestView,
    PasswordResetView,
)

app_name = "user"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path(
        "api/password-reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "api/password-reset/confirm/",
        PasswordResetView.as_view(),
        name="password-reset-confirm",
    ),
]
