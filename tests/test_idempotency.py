from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.events import EventEnvelope
from src.idempotency import (
    IdempotencyStoreError,
    InMemoryIdempotencyStore,
    RedisIdempotencyStore,
)
from src.models import Trade
from src.persistence.memory import InMemoryUnitOfWork
from src.services.event_processing import TradeExecutedProcessor
from src.services.trade_posting import TradePostingService


def event(trade_id: int = 1, key: str | None = None) -> EventEnvelope:
    trade = Trade(trade_id, 100 + trade_id, "AAPL", "BUY", Decimal("10.25"), 2,
                  datetime(2026, 1, 1, tzinfo=timezone.utc))
    envelope = EventEnvelope.trade_executed(trade, "correlation-1")
    if key is None:
        return envelope
    return EventEnvelope(envelope.event_id, envelope.event_type, envelope.schema_version,
                         envelope.occurred_at, envelope.correlation_id, key, envelope.payload)


def processor():
    unit_of_work = InMemoryUnitOfWork()
    service = TradePostingService(lambda: unit_of_work)
    return TradeExecutedProcessor(InMemoryIdempotencyStore(), service), unit_of_work


def test_first_event_processes_and_duplicate_cannot_double_post():
    service, unit_of_work = processor()
    first = event()

    assert service.process(first).processed is True
    assert service.process(first).reason == "duplicate"
    assert len(unit_of_work.ledger.for_reference("trade:1")) == 2


def test_different_event_processes():
    service, unit_of_work = processor()
    assert service.process(event(1)).processed is True
    assert service.process(event(2)).processed is True
    assert unit_of_work.trades.get(2) is not None


def test_same_idempotency_key_with_different_payload_cannot_double_post():
    service, unit_of_work = processor()
    assert service.process(event(1, "fixed-key")).processed is True
    assert service.process(event(2, "fixed-key")).processed is False
    assert unit_of_work.trades.get(2) is None


def test_failed_processing_releases_claim_for_retry():
    store = InMemoryIdempotencyStore()

    class FailingPostingService:
        def post(self, trade):
            raise RuntimeError("database unavailable")

    service = TradeExecutedProcessor(store, FailingPostingService())
    with pytest.raises(RuntimeError):
        service.process(event())
    assert store.claim("trade:1") is True


def test_redis_uses_atomic_set_nx_and_surfaces_failure():
    class RedisDouble:
        def __init__(self):
            self.calls = []

        def set(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            return True

        def delete(self, key):
            return 1

    client = RedisDouble()
    store = RedisIdempotencyStore(client)
    assert store.claim("trade:1", ttl_seconds=60) is True
    assert client.calls == [(('idempotency:trade:1', 'claimed'), {'nx': True, 'ex': 60})]

    class BrokenRedis:
        def set(self, *args, **kwargs):
            raise ConnectionError("offline")

    with pytest.raises(IdempotencyStoreError, match="claim failed"):
        RedisIdempotencyStore(BrokenRedis()).claim("trade:1")
