from celery import shared_task
import random
import requests
import logging
from .otp_handler import store_otp, normalize_phone
from . import OTP_SETTINGS

logger = logging.getLogger(__name__)

@shared_task
def send_sms_code(phone_number, code):
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain",
        "x-api-key": str(OTP_SETTINGS["SMS_API_KEY"]),
    }

    payload = {
        "mobile": phone_number,
        "templateId": int(OTP_SETTINGS["SMS_TEMPLATE_ID"]),
        "parameters": [{"name": "CODE", "value": code}],
    }

    try:
        response = requests.post('https://api.sms.ir/v1/send/verify',
                                 json=payload, headers=headers, timeout=10)
        data = response.json()
        logger.warning(f"SMS.ir response for {phone_number}: {data}")
        return {"success": data.get("status") == 1, "data": data}
    except Exception as e:
        logger.error(f"SMS sending failed for {phone_number}: {e}")
        return {"success": False, "error": str(e)}

def send_otp_to_user(phone_number, purpose="login"):
    phone_number = normalize_phone(phone_number)
    code = str(random.randint(100000, 999999))
    store_otp(phone_number, purpose.lower(), code)
    send_sms_code.delay(phone_number, code)
    return code
