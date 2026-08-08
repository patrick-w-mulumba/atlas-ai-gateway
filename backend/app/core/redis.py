from redis.asyncio import Redis

from app.core.config import get_settings


settings = get_settings()

REDIS_URL = "redis://localhost:6379/0"

redis_client = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)