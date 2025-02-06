import logging
from functools import lru_cache

from shared_utils.settings import Settings


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
