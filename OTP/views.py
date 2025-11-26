from django.shortcuts import render
import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .otp_handler import verify_code_from_redis, can_send_otp, normalize_phone
from . import serializers
from .tasks import send_otp_to_user
from django.contrib.auth import get_user_model


User = get_user_model()


def send_otp(user, purpose="SIGNUP"):
    code = f"{random.randint(100000, 999999)}"
    verify_code_from_redis(user.phone_number, purpose, code)

    print(f"🔑 OTP for {user.phone_number} is {code}")

    return code

@api_view(["POST"])
def send_otp_view(request):
    serializer = serializers.SendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    raw_phone = serializer.validated_data['phone_number']
    phone_number = normalize_phone(raw_phone)

    if not can_send_otp(phone_number, purpose="LOGIN"):
        return Response(
            {"error": "شما بیش از حد مجاز درخواست OTP داده‌اید. لطفاً بعداً دوباره تلاش کنید."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # دیگر کاربری ساخته نمی‌شود؛ فقط OTP ساخته و ارسال می‌شود
    otp = send_otp_to_user(phone_number, purpose="LOGIN")

    # در Production هیچ‌وقت OTP را در پاسخ برنگردان
    return Response({
        "message": "کد تایید ارسال شد.",
        'OTP': otp
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
def verify_otp_view(request):
    serializer = serializers.VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    raw_phone = serializer.validated_data['phone_number']
    code = serializer.validated_data['code']

    phone_number = normalize_phone(raw_phone)

    result = verify_code_from_redis(phone_number, "LOGIN", code)
    if result == "too_many_attempts":
        return Response(
            {"error": "تعداد تلاش‌های شما بیش از حد مجاز است. لطفاً بعداً تلاش کنید."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    elif result == "invalid_code":
        return Response({"error": "کد نامعتبر یا منقضی شده است."},
                        status=status.HTTP_400_BAD_REQUEST)

    user, created = User.objects.get_or_create(
        phone_number=phone_number,
        defaults={

        }
    )


    refresh = RefreshToken.for_user(user)
    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "created": created , # برای اطلاع (اختیاری)
        "code": code
    }, status=status.HTTP_200_OK)