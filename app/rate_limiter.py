from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def custom_key_func(request):
    # Логируем каждый запрос и его IP
    client_ip = request.client.host
    logger.debug(f"Rate limit request from IP: {client_ip}")
    return client_ip

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    retry_after="human_readable",
)
