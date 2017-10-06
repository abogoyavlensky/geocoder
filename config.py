"""
    config.py
    ~~~~~~~~~

    Service app configuration.

    :copyright: (c) 2017 by Andrey Bogoyavlensky.
"""
from envparse import Env
from flask_redis import FlaskRedis
from mockredis import MockRedis


# Mock redis store for testing
class MockRedisWrapper(MockRedis):
    """A wrapper to add the `from_url` classmethod"""

    @classmethod
    def from_url(cls, *args, **kwargs):
        return cls()


# Config
env = Env()
env.read_envfile()

BACKEND_URL = env('BACKEND_URL', default='http://backend/')
DEFAULT_TIMEOUT = 0.4
RETRY_ATTEMPTS = 3
MAX_TIMEOUT = 2
ASSUMPTION = 0.05
MAX_RETRY_TIMEOUT = MAX_TIMEOUT - (DEFAULT_TIMEOUT + ASSUMPTION)
CACHE_EXPIRATION = env('CACHE_EXPIRATION', default=5)
IS_CACHE_ENABLED = env.bool('IS_CACHE_ENABLED', default=True)
API_ERRORS = ['OVER_QUERY_LIMIT']

if env.bool('TESTING', default=False):
    redis_store = FlaskRedis.from_custom_provider(MockRedisWrapper)
else:
    redis_store = FlaskRedis()
