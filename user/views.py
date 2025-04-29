from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
import logging

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
)

logger = logging.getLogger(__name__)


class CreateUserView(generics.CreateAPIView):
    """API view to create a new user."""

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user with email, password, first_name, and last_name.",
        responses={201: UserSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CreateTokenView(TokenObtainPairView):
    """API view to obtain JWT token."""

    serializer_class = AuthTokenSerializer
    throttle_scope = "login"

    @extend_schema(
        summary="Obtain JWT token",
        description="Authenticates a user with email and password, returning access and refresh tokens.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """API view to retrieve or update authenticated user details."""

    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Manage authenticated user",
        description="Retrieve or update the authenticated user's profile.",
    )
    def get_object(self):
        return self.request.user


class PasswordResetRequestView(generics.GenericAPIView):
    """API view to request a password reset email.

    Expects a POST request with an email in the request body.
    If the email is valid, sends a password reset email.
    """

    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    throttle_scope = "password_reset"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"detail": _("Password reset email sent.")},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                logger.error(f"Error sending password reset email: {str(e)}")
                return Response(
                    {"detail": _("An error occurred while processing your request.")},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    """API view to reset a user's password.

    Expects a POST request with a token and new password.
    If the token is valid, resets the user's password.
    """

    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"detail": _("Password has been reset.")}, status=status.HTTP_200_OK
                )
            except Exception as e:
                logger.error(f"Error resetting password: {str(e)}")
                return Response(
                    {"detail": _("An error occurred while processing your request.")},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
