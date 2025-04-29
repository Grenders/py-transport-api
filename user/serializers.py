from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import serializers
from django.utils.translation import gettext as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
import re

from user.models import PasswordResetToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "is_staff")
        read_only_fields = (
            "id",
            "is_staff",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "style": {"input_type": "password"},
                "label": _("Password"),
            }
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        password = validated_data.get("password")

        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        validated_data["email"] = get_user_model().objects.normalize_email(
            validated_data["email"]
        )

        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(TokenObtainPairSerializer):
    email = serializers.CharField(label=_("Email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )

            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        data = super().validate(attrs)
        return data


# Example for reset request
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = get_user_model().objects.get(email=value)
        except get_user_model().DoesNotExist:
            pass
        return value

    def save(self):
        reset_token = PasswordResetToken.objects.create(user=self.user)
        reset_url = f"http://example.com/reset-password/{reset_token.token}/"
        send_mail(
            _("Password reset request"),
            _("Click the following link to reset your password: ") + reset_url,
            "from@example.com",
            [self.user.email],
            fail_silently=False,
        )


# Example
class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate_token(self, value):
        try:
            reset_token = PasswordResetToken.objects.get(
                token=value, expires_at__gt=timezone.now()
            )
            self.user = reset_token.user
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError(_("Invalid or expired token"))
        return value

    @staticmethod
    def validate_new_password(value):
        if len(value) < 8:
            raise serializers.ValidationError(
                _("Password must be at least 8 characters long")
            )
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                _("Password must contain at least one uppercase letter")
            )
        if not re.search(r"\d", value):
            raise serializers.ValidationError(
                _("Password must contain at least one digit")
            )
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError(
                _("Password must contain at least one special character")
            )
        return value

    def save(self):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()
        PasswordResetToken.objects.filter(token=self.validated_data["token"]).delete()
