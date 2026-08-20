from src.events import EventEnvelope
from src.transport.contracts import TransportMessage
from src.transport.serialization import serialize_event


class KafkaEventProducer:
    """Adapter compatible with clients exposing `produce` (for example confluent-kafka)."""

    def __init__(self, client):
        self._client = client

    def publish(self, topic: str, event: EventEnvelope) -> None:
        self._client.produce(
            topic=topic,
            key=event.idempotency_key.encode(),
            value=serialize_event(event),
            headers={"correlation_id": event.correlation_id, "event_id": event.event_id},
        )


class KafkaEventConsumer:
    def __init__(self, client, timeout_seconds: float = 1.0):
        self._client = client
        self._timeout_seconds = timeout_seconds

    def poll(self) -> TransportMessage | None:
        message = self._client.poll(self._timeout_seconds)
        if message is None:
            return None
        if message.error():
            raise RuntimeError(str(message.error()))
        headers = {key: value.decode() for key, value in (message.headers() or [])}
        return TransportMessage(message.value(), message.key(), headers)
