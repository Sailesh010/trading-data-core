from dataclasses import dataclass, field
from typing import Protocol

from src.events import EventEnvelope


@dataclass(frozen=True)
class TransportMessage:
    value: bytes
    key: bytes | None = None
    headers: dict[str, str] = field(default_factory=dict)


class EventProducer(Protocol):
    def publish(self, topic: str, event: EventEnvelope) -> None: ...


class EventConsumer(Protocol):
    def poll(self) -> TransportMessage | None: ...
