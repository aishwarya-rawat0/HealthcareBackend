from django.conf import settings
from django.core.mail import send_mail


def send_verification_email(user, code):
    send_mail(
        subject="Verify your email",
        message=(
            f"Hi {user.name},\n\n"
            f"Your OTP is {code}. It expires in {settings.OTP_EXPIRY_MINUTES} minutes.\n\n"
            "If you didn't create an account, you can ignore this email."
        ),
        from_email=None,
        recipient_list=[user.email],
    )
