from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
import uuid

from .models import User, PasswordResetToken


class UserModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        email = "test@EXAMPLE.com"
        password = "Testpass123"
        user = User.objects.create_user(
            email=email, password=password, first_name="John", last_name="Doe"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_no_email_raises_error(self):
        with self.assertRaisesMessage(ValueError, "The given email must be set"):
            User.objects.create_user(email=None, password="pass")

    def test_create_user_invalid_email_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            User.objects.create_user(email="invalid-email", password="pass")

    def test_create_superuser(self):
        email = "super@Example.com"
        user = User.objects.create_superuser(
            email=email, password="pass", first_name="A", last_name="B"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_superuser_with_is_staff_false_raises(self):
        with self.assertRaisesMessage(ValueError, "Superuser must have is_staff=True."):
            User.objects.create_superuser(
                email="super@example.com",
                password="pass",
                first_name="A",
                last_name="B",
                is_staff=False,
            )

    def test_create_superuser_with_is_superuser_false_raises(self):
        with self.assertRaisesMessage(
            ValueError, "Superuser must have is_superuser=True."
        ):
            User.objects.create_superuser(
                email="super@example.com",
                password="pass",
                first_name="A",
                last_name="B",
                is_superuser=False,
            )


class PasswordResetTokenModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="usr@example.com", password="pass", first_name="A", last_name="B"
        )

    def test_token_and_expiry_set_on_save(self):
        token = PasswordResetToken(user=self.user)
        self.assertIsNone(token.token)
        self.assertIsNone(token.expires_at)
        token.save()

        self.assertIsNotNone(token.token)
        self.assertEqual(len(token.token), 32)
        uuid.UUID(token.token, version=4)

        expected = timezone.now() + timedelta(hours=1)
        self.assertAlmostEqual(token.expires_at, expected, delta=timedelta(seconds=5))

    def test_is_expired_returns_false_for_valid_token(self):
        token = PasswordResetToken.objects.create(user=self.user)
        self.assertFalse(token.is_expired())

    def test_is_expired_returns_true_for_expired_token(self):
        past_time = timezone.now() - timedelta(hours=2)
        token = PasswordResetToken(
            user=self.user, token=uuid.uuid4().hex, expires_at=past_time
        )
        token.save()
        self.assertTrue(token.is_expired())
