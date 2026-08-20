import json
from datetime import datetime
from typing import Any

from src.events import EventEnvelope


class SchemaValidationError(ValueError):
    pass


REQUIRED_ENVELOPE_FIELDS = {
    "event_id", "event_type", "schema_version", "occurred_at",
    "correlation_id", "idempotency_key", "payload",
}
REQUIRED_TRADE_FIELDS = {
    "trade_id", "order_id", "symbol", "side", "price", "quantity", "timestamp",
}


def serialize_event(event: EventEnvelope) -> bytes:
    return json.dumps(
        {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "schema_version": event.schema_version,
            "occurred_at": event.occurred_at,
            "correlation_id": event.correlation_id,
            "idempotency_key": event.idempotency_key,
            "payload": event.payload,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def deserialize_event(raw: bytes) -> EventEnvelope:
    try:
        document: Any = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SchemaValidationError("event is not valid UTF-8 JSON") from exc
    if not isinstance(document, dict):
        raise SchemaValidationError("event envelope must be an object")
    missing = REQUIRED_ENVELOPE_FIELDS - document.keys()
    if missing:
        raise SchemaValidationError(f"missing envelope fields: {sorted(missing)}")
    if document["event_type"] != "TradeExecuted" or document["schema_version"] != 1:
        raise SchemaValidationError("unsupported event type or schema version")
    if not isinstance(document["payload"], dict):
        raise SchemaValidationError("payload must be an object")
    payload_missing = REQUIRED_TRADE_FIELDS - document["payload"].keys()
    if payload_missing:
        raise SchemaValidationError(f"missing trade fields: {sorted(payload_missing)}")
    if document["payload"]["side"] not in {"BUY", "SELL"}:
        raise SchemaValidationError("trade side must be BUY or SELL")
    try:
        datetime.fromisoformat(document["occurred_at"])
        timestamp = datetime.fromisoformat(document["payload"]["timestamp"])
    except (TypeError, ValueError) as exc:
        raise SchemaValidationError("timestamps must be ISO-8601") from exc
    if timestamp.tzinfo is None:
        raise SchemaValidationError("trade timestamp must include a timezone")
    return EventEnvelope(**document)
