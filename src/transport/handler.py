from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.events import EventEnvelope
from src.idempotency import IdempotencyStoreError
from src.services.event_processing import ProcessingResult, TradeExecutedProcessor
from src.transport.contracts import TransportMessage
from src.transport.serialization import deserialize_event


class RetryableProcessingError(RuntimeError):
    pass


class ObservabilityHook(Protocol):
    def __call__(self, event_name: str, attributes: dict[str, object]) -> None: ...


@dataclass(frozen=True)
class DeadLetterRecord:
    original: TransportMessage
    error_type: str
    error_message: str
    attempts: int


class InMemoryDeadLetterSink:
    def __init__(self):
        self.records: list[DeadLetterRecord] = []

    def write(self, record: DeadLetterRecord) -> None:
        self.records.append(record)


class ConsumerHandler:
    def __init__(
        self,
        processor: TradeExecutedProcessor,
        dead_letter_sink,
        *,
        max_attempts: int = 3,
        observe: ObservabilityHook | None = None,
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least one")
        self._processor = processor
        self._dead_letter_sink = dead_letter_sink
        self._max_attempts = max_attempts
        self._observe = observe or (lambda event_name, attributes: None)

    def handle(self, message: TransportMessage) -> ProcessingResult | None:
        event: EventEnvelope | None = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                event = deserialize_event(message.value)
                self._observe("event.received", self._metadata(event, attempt))
                result = self._processor.process(event)
                self._observe("event.processed", {**self._metadata(event, attempt),
                                                   "result": result.reason})
                return result
            except (RetryableProcessingError, IdempotencyStoreError) as exc:
                self._observe("event.retry", self._error_metadata(event, message, attempt, exc))
                if attempt == self._max_attempts:
                    self._dead_letter(message, event, attempt, exc)
            except Exception as exc:
                self._dead_letter(message, event, attempt, exc)
                return None
        return None

    def _dead_letter(self, message, event, attempt, exc) -> None:
        self._dead_letter_sink.write(DeadLetterRecord(
            original=message,
            error_type=type(exc).__name__,
            error_message=str(exc),
            attempts=attempt,
        ))
        self._observe("event.dead_lettered", self._error_metadata(event, message, attempt, exc))

    @staticmethod
    def _metadata(event: EventEnvelope, attempt: int) -> dict[str, object]:
        return {"event_id": event.event_id, "correlation_id": event.correlation_id,
                "idempotency_key": event.idempotency_key, "attempt": attempt}

    @staticmethod
    def _error_metadata(event, message, attempt, exc) -> dict[str, object]:
        return {
            "event_id": event.event_id if event else message.headers.get("event_id"),
            "correlation_id": event.correlation_id if event else message.headers.get("correlation_id"),
            "attempt": attempt,
            "error_type": type(exc).__name__,
        }
