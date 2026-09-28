from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "name", "email", "password")
        extra_kwargs = {"email": {"validators": []}}

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value, is_email_verified=True).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.filter(email=validated_data["email"], is_email_verified=False).first()
        if user is None:
            return User.objects.create_user(**validated_data)
        user.name = validated_data["name"]
        user.set_password(validated_data["password"])
        user.save(update_fields=["name", "password"])
        return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.RegexField(r"^\d{6}$", error_messages={"invalid": "OTP must be 6 digits."})

    def validate(self, attrs):
        user = User.objects.filter(email=attrs["email"].lower()).first()
        if user is None or not user.check_verification_code(attrs["otp"]):
            raise serializers.ValidationError("Invalid or expired OTP.")
        attrs["user"] = user
        return attrs


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_email_verified:
            raise AuthenticationFailed("Please verify your email before logging in.")
        return data
