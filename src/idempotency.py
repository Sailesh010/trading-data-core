from __future__ import annotations

from threading import Lock
from typing import Protocol


class IdempotencyStoreError(RuntimeError):
    """The idempotency decision could not be made safely."""


class IdempotencyStore(Protocol):
    def claim(self, key: str, ttl_seconds: int | None = None) -> bool: ...

    def release(self, key: str) -> None: ...


class InMemoryIdempotencyStore:
    def __init__(self):
        self._claimed: set[str] = set()
        self._lock = Lock()

    def claim(self, key: str, ttl_seconds: int | None = None) -> bool:
        del ttl_seconds  # Deterministic test store intentionally does not expire claims.
        with self._lock:
            if key in self._claimed:
                return False
            self._claimed.add(key)
            return True

    def release(self, key: str) -> None:
        with self._lock:
            self._claimed.discard(key)


class RedisIdempotencyStore:
    """Redis SET NX adapter dedicated to financial-event deduplication."""

    def __init__(self, client, *, key_prefix: str = "idempotency:"):
        self._client = client
        self._key_prefix = key_prefix

    def claim(self, key: str, ttl_seconds: int | None = None) -> bool:
        try:
            options = {"nx": True}
            if ttl_seconds is not None:
                if ttl_seconds <= 0:
                    raise ValueError("ttl_seconds must be positive")
                options["ex"] = ttl_seconds
            return bool(self._client.set(f"{self._key_prefix}{key}", "claimed", **options))
        except ValueError:
            raise
        except Exception as exc:
            raise IdempotencyStoreError("Redis idempotency claim failed") from exc

    def release(self, key: str) -> None:
        try:
            self._client.delete(f"{self._key_prefix}{key}")
        except Exception as exc:
            raise IdempotencyStoreError("Redis idempotency release failed") from exc
