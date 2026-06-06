"""Token-bucket rate limiting.

Part of Discord AI Bot by Viprasol Tech Private Limited (https://viprasol.com).

A small, dependency-free token-bucket limiter used to throttle how often a given
key (typically a user or channel id) may trigger the LLM. The clock is
injectable so the limiter can be tested deterministically without sleeping.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(slots=True)
class _Bucket:
    tokens: float
    last: float


class RateLimiter:
    """A per-key token-bucket rate limiter.

    Each key gets its own bucket holding up to ``capacity`` tokens that refill at
    ``refill_rate`` tokens per second. Every accepted action costs one token.

    Args:
        capacity: Maximum burst size (tokens a fresh bucket starts with). Must
            be positive.
        refill_rate: Tokens added per second. Must be positive.
        clock: Monotonic time source, injectable for testing. Defaults to
            :func:`time.monotonic`.

    Raises:
        ValueError: If ``capacity`` or ``refill_rate`` is not positive.
    """

    def __init__(
        self,
        capacity: float,
        refill_rate: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialise the limiter; see the class docstring for argument details."""
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")
        self._capacity = float(capacity)
        self._rate = float(refill_rate)
        self._clock = clock
        self._buckets: dict[str, _Bucket] = {}

    def _refill(self, bucket: _Bucket, now: float) -> None:
        elapsed = now - bucket.last
        if elapsed > 0:
            bucket.tokens = min(self._capacity, bucket.tokens + elapsed * self._rate)
            bucket.last = now

    def allow(self, key: str, cost: float = 1.0) -> bool:
        """Try to consume ``cost`` tokens for ``key``.

        Returns:
            ``True`` if enough tokens were available (and were consumed),
            ``False`` otherwise (no tokens are consumed on rejection).
        """
        now = self._clock()
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self._capacity, last=now)
            self._buckets[key] = bucket
        else:
            self._refill(bucket, now)
        if bucket.tokens >= cost:
            bucket.tokens -= cost
            return True
        return False

    def tokens_available(self, key: str) -> float:
        """Return the current token count for ``key`` after refilling."""
        now = self._clock()
        bucket = self._buckets.get(key)
        if bucket is None:
            return self._capacity
        self._refill(bucket, now)
        return bucket.tokens

    def reset(self, key: str | None = None) -> None:
        """Reset one key's bucket, or all buckets when ``key`` is ``None``."""
        if key is None:
            self._buckets.clear()
        else:
            self._buckets.pop(key, None)
