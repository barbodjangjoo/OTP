from . import OTP_SETTINGS
from .redis_client import redis_client
from datetime import timedelta

DEFAULT_VERIFY_MAX_ATTEMPTS = OTP_SETTINGS["MAX_ATTEMPTS"]
DEFAULT_VERIFY_ATTEMPT_TTL = OTP_SETTINGS["DEFAULT_TTL"]
DEFAULT_OTP_TTL = OTP_SETTINGS["DEFAULT_TTL"]
DEFAULT_MAX_SEND = OTP_SETTINGS["MAX_SENDS"]
DEFAULT_SEND_TTL = OTP_SETTINGS["DEFAULT_TTL"]


def normalize_phone(phone):
    phone = phone.strip()
    if phone.startswith("+98"):
        phone = "0" + phone[3:]
    return phone


def _otp_key(purpose, phone_number):
    return f"otp:{purpose.lower()}:{normalize_phone(phone_number)}"

def _attempt_key(purpose, phone_number):
    return f"otp:attempt:{purpose.lower()}:{normalize_phone(phone_number)}"

def _send_key(purpose, phone_number):
    return f"otp:send:{purpose.lower()}:{normalize_phone(phone_number)}"


# بررسی اینکه آیا می‌توان OTP فرستاد
def can_send_otp(phone_number, purpose="LOGIN",
                 max_send=DEFAULT_MAX_SEND,
                 send_ttl=DEFAULT_SEND_TTL):
    phone_number = normalize_phone(phone_number)
    key = _send_key(purpose, phone_number)
    sends = redis_client.get(key)
    if sends and int(sends) >= max_send:
        return False
    new_sends = redis_client.incr(key)
    if new_sends == 1:
        redis_client.expire(key, send_ttl)
    return True


# ذخیره OTP
def store_otp(phone_number, purpose, code, otp_ttl=DEFAULT_OTP_TTL):
    phone_number = normalize_phone(phone_number)
    key = _otp_key(purpose, phone_number)
    redis_client.setex(key, otp_ttl, str(code).strip())


# بررسی کد وارد شده
def verify_code_from_redis(phone_number, purpose, code,
                           max_attempts=DEFAULT_VERIFY_MAX_ATTEMPTS,
                           attempt_ttl=DEFAULT_VERIFY_ATTEMPT_TTL):
    phone_number = normalize_phone(phone_number)
    purpose = purpose.lower()
    attempt_key = _attempt_key(purpose, phone_number)
    otp_key = _otp_key(purpose, phone_number)

    # خواندن تعداد تلاش‌ها
    attempts = redis_client.get(attempt_key)
    if attempts and int(attempts) >= max_attempts:
        return "too_many_attempts"

    # افزایش شمارنده تلاش
    new_attempts = redis_client.incr(attempt_key)
    if new_attempts == 1:
        redis_client.expire(attempt_key, attempt_ttl)

    # بررسی OTP
    stored_code = redis_client.get(otp_key)
    if stored_code and stored_code.strip() == str(code).strip():
        redis_client.delete(otp_key)
        redis_client.delete(attempt_key)
        return "success"

    return "invalid_code"

