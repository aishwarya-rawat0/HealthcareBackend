import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_email_verified", True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=128, blank=True)
    verification_code_expires_at = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email

    def set_verification_code(self):
        code = f"{secrets.randbelow(1_000_000):06d}"
        self.verification_code = make_password(code)
        self.verification_code_expires_at = timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        self.save(update_fields=["verification_code", "verification_code_expires_at"])
        return code

    def check_verification_code(self, code):
        if not self.verification_code or not self.verification_code_expires_at:
            return False
        if timezone.now() > self.verification_code_expires_at:
            return False
        return check_password(code, self.verification_code)

    def mark_email_verified(self):
        self.is_email_verified = True
        self.verification_code = ""
        self.verification_code_expires_at = None
        self.save(update_fields=["is_email_verified", "verification_code", "verification_code_expires_at"])
