"""One boto3 Session + a client factory with adaptive retries.

- Session is created lazily: importing this module makes no network call.
- retries mode="adaptive" = standard retries (exponential backoff + jitter) plus a client-side
  rate limiter that slows down after throttling errors.
  Catch: the limiter is per client object, so share clients instead of creating one per request.
"""

from functools import lru_cache
from typing import Any

import boto3
from botocore.config import Config

from app.shared.config import get_settings

RETRY_CONFIG = Config(
    retries={"max_attempts": 5, "mode": "adaptive"},
    connect_timeout=3,
    read_timeout=10,
)


@lru_cache
def session() -> boto3.session.Session:
    # Default credential chain: env -> shared profile -> web identity -> container/instance role.
    return boto3.session.Session(region_name=get_settings().aws_region)


@lru_cache
def client(service: str) -> Any:
    """Cached low-level client per service (clients are thread-safe; sessions are not)."""
    return session().client(service, config=RETRY_CONFIG)


@lru_cache
def resource(service: str) -> Any:
    """Cached high-level resource (DynamoDB, S3). Resources are NOT thread-safe: one per thread in real apps."""
    return session().resource(service, config=RETRY_CONFIG)
