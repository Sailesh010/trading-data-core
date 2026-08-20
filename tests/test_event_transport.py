from datetime import datetime, timezone
from decimal import Decimal

from src.events import EventEnvelope
from src.idempotency import InMemoryIdempotencyStore
from src.models import Trade
from src.persistence.memory import InMemoryUnitOfWork
from src.services.event_processing import TradeExecutedProcessor
from src.services.trade_events import TradeEventPublisher
from src.services.trade_posting import TradePostingService
from src.transport.contracts import TransportMessage
from src.transport.handler import (
    ConsumerHandler,
    InMemoryDeadLetterSink,
    RetryableProcessingError,
)
from src.transport.memory import InMemoryEventProducer
from src.transport.serialization import deserialize_event, serialize_event


def envelope() -> EventEnvelope:
    trade = Trade(1, 10, "AAPL", "BUY", Decimal("12.3400"), 3,
                  datetime(2026, 1, 1, tzinfo=timezone.utc))
    return EventEnvelope.trade_executed(trade, "corr-123")


def working_handler(observations=None):
    uow = InMemoryUnitOfWork()
    processor = TradeExecutedProcessor(
        InMemoryIdempotencyStore(), TradePostingService(lambda: uow))
    dlq = InMemoryDeadLetterSink()
    observation_log = observations if observations is not None else []
    handler = ConsumerHandler(
        processor, dlq,
        observe=lambda name, attributes: observation_log.append((name, attributes)),
    )
    return handler, uow, dlq


def test_trade_event_serialization_round_trip_preserves_metadata():
    event = envelope()
    decoded = deserialize_event(serialize_event(event))
    assert decoded == event
    assert decoded.correlation_id == "corr-123"


def test_producer_propagates_correlation_headers():
    producer = InMemoryEventProducer()
    event = TradeEventPublisher(producer).publish(
        Trade(1, 10, "AAPL", "BUY", Decimal("1.00"), 1,
              datetime(2026, 1, 1, tzinfo=timezone.utc)), "corr-123")
    topic, message = producer.messages[0]
    assert topic == "trades.executed.v1"
    assert message.headers == {"correlation_id": "corr-123", "event_id": event.event_id}


def test_success_and_duplicate_delivery_are_replay_safe():
    handler, uow, dlq = working_handler()
    message = TransportMessage(serialize_event(envelope()))
    assert handler.handle(message).processed is True
    assert handler.handle(message).reason == "duplicate"
    assert len(uow.ledger.for_reference("trade:1")) == 2
    assert dlq.records == []


def test_malformed_and_non_retryable_events_go_directly_to_dlq():
    handler, _, dlq = working_handler()
    assert handler.handle(TransportMessage(b'{"bad":true}')) is None
    assert dlq.records[0].error_type == "SchemaValidationError"
    assert dlq.records[0].attempts == 1


def test_retryable_failure_retries_then_dead_letters_with_metadata():
    class FailingProcessor:
        def __init__(self):
            self.calls = 0

        def process(self, event):
            self.calls += 1
            raise RetryableProcessingError("database timeout")

    observations = []
    processor = FailingProcessor()
    dlq = InMemoryDeadLetterSink()
    handler = ConsumerHandler(
        processor, dlq, max_attempts=3,
        observe=lambda name, attributes: observations.append((name, attributes)),
    )
    message = TransportMessage(serialize_event(envelope()), headers={"correlation_id": "corr-123"})
    assert handler.handle(message) is None
    assert processor.calls == 3
    assert dlq.records[0].attempts == 3
    assert observations[-1][0] == "event.dead_lettered"
    assert observations[-1][1]["correlation_id"] == "corr-123"


def test_non_retryable_processing_failure_is_not_retried():
    class InvalidProcessor:
        def process(self, event):
            raise ValueError("invalid account")

    dlq = InMemoryDeadLetterSink()
    handler = ConsumerHandler(InvalidProcessor(), dlq, max_attempts=3)
    assert handler.handle(TransportMessage(serialize_event(envelope()))) is None
    assert dlq.records[0].attempts == 1
