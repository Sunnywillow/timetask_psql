import redis
from .config import REDIS_DB_URL


def connect_redis():
    return redis.Redis(REDIS_DB_URL)
