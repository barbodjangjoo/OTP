OTP Django App

A lightweight and pluggable Django application that provides One-Time Password (OTP) functionality for phone/email verification, passwordless login, and two-factor authentication. The app stores short-lived OTP codes in Redis and optionally uses Celery for background delivery.

Features

- Time-limited OTP generation

- Redis-based storage with configurable TTL

- Pluggable delivery handler (SMS, Email, etc.)

- OTP verification endpoint

- Resend endpoint with rate-limiting support

- Optional async sending via Celery

- Fully compatible with Django REST Framework

OTP/
│
├── urls.py            # OTP endpoints
├── views.py           # Send/Verify/Resend logic
├── serializers.py     # DRF serializers
├── otp_handler.py     # OTP generator + sending handler
├── redis_client.py    # Interactions with Redis (set/get/TTL)
├── tasks.py           # Celery tasks
└── models.py          # Optional database models


Quick Start
1. Add app to Django

    INSTALLED_APPS = [
        # ...
        'OTP',
    ]

2. Configure Redis & Celery (optional)

    REDIS_URL=redis://localhost:6379/0
    CELERY_BROKER_URL=redis://localhost:6379/1
    CELERY_RESULT_BACKEND=redis://localhost:6379/2

3. Include URLs

from django.urls import path, include

    urlpatterns = [
        path('otp/', include('OTP.urls')),
    ]

API Endpoints

    POST /otp/send/
    Generate and send OTP.

    POST /otp/verify/
    Verify OTP code.

    POST /otp/resend/
    Resend existing or newly generated OTP.

Example: Send OTP

    curl -X POST http://localhost:8000/otp/send/ \
    -H "Content-Type: application/json" \
    -d '{"destination":"+15555551234","channel":"sms"}'

Example: Verify OTP

    curl -X POST http://localhost:8000/otp/verify/ \
    -H "Content-Type: application/json" \
    -d '{"destination":"+15555551234","code":"123456"}'

Integration Notes
Custom Delivery Handler

Extend or modify otp_handler.py:

def send_otp(destination, code, channel="sms"):
    # Integrate with Twilio, AWS SNS, Kavenegar, SMTP, etc.
    pass


Redis Configuration

redis_client.py controls:

- OTP TTL

- Code storage format

- Rate-limit counting

- Key structure

Modify constants inside it to adjust behavior.
Rate Limiting

Can be implemented through:

- DRF throttling

- Custom Redis counters

- Logic inside otp_handler or views

Tests

python manage.py test OTP


Security Notes:
- Use HTTPS in production

- Use secure random OTP generation

- Consider hashing OTPs in Redis

- Enforce resend/attempt rate limits

- Avoid logging OTPs

- Consider user lockouts after repeated failures

Requirements (Suggested)

    Django>=4.0
    redis
    celery
    djangorestframework

Local Development (macOS)
    brew install redis
    brew services start redis
    python manage.py runserver

Customization
You can adjust OTP length or format in otp_handler.py:

import random

def generate_otp(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


