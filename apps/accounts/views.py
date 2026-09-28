from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .emails import send_verification_email
from .models import User
from .serializers import LoginSerializer, RegisterSerializer, ResendOTPSerializer, VerifyOTPSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = serializer.save()
            send_verification_email(user, user.set_verification_code())
        return Response(
            {
                "message": "User registered successfully. Check your email for the OTP.",
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["user"].mark_email_verified()
        return Response({"message": "Email verified. You can now log in."})


class ResendOTPView(generics.GenericAPIView):
    serializer_class = ResendOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email=serializer.validated_data["email"].lower()).first()
        if user and not user.is_email_verified:
            send_verification_email(user, user.set_verification_code())
        return Response({"message": "If that account exists and isn't verified yet, a new OTP has been sent."})


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
