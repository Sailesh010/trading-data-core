from collections import deque

from src.events import EventEnvelope
from src.transport.contracts import TransportMessage
from src.transport.serialization import serialize_event


class InMemoryEventProducer:
    def __init__(self):
        self.messages: list[tuple[str, TransportMessage]] = []

    def publish(self, topic: str, event: EventEnvelope) -> None:
        self.messages.append((topic, TransportMessage(
            value=serialize_event(event),
            key=event.idempotency_key.encode(),
            headers={"correlation_id": event.correlation_id, "event_id": event.event_id},
        )))


class InMemoryEventConsumer:
    def __init__(self, messages=()):
        self._messages = deque(messages)

    def poll(self) -> TransportMessage | None:
        return self._messages.popleft() if self._messages else None
