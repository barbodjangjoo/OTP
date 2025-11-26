import redis
from . import OTP_SETTINGS

redis_client = redis.StrictRedis(
    host=OTP_SETTINGS["REDIS_HOST"],
    port=OTP_SETTINGS["REDIS_PORT"],
    db=OTP_SETTINGS["REDIS_DB"],
    decode_responses=True
)
