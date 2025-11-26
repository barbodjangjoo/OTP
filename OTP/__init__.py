from django.conf import settings

OTP_SETTINGS = {
    "REDIS_HOST": getattr(settings, "OTP_REDIS_HOST", "redis"),
    "REDIS_PORT": getattr(settings, "OTP_REDIS_PORT", 6379),
    "REDIS_DB": getattr(settings, "OTP_REDIS_DB", 1),

    "DEFAULT_TTL": getattr(settings, "OTP_DEFAULT_TTL", 300),
    "MAX_SENDS": getattr(settings, "OTP_MAX_SENDS", 3),
    "MAX_ATTEMPTS": getattr(settings, "OTP_MAX_ATTEMPTS", 3),

    "SMS_API_KEY": getattr(settings, "OTP_SMS_API_KEY", None),
    "SMS_TEMPLATE_ID": getattr(settings, "OTP_SMS_TEMPLATE_ID", None),
}
