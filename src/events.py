from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any
from uuid import uuid4

from src.models import Trade


@dataclass(frozen=True)
class EventEnvelope:
    event_id: str
    event_type: str
    schema_version: int
    occurred_at: str
    correlation_id: str
    idempotency_key: str
    payload: Dict[str, Any]

    @staticmethod
    def trade_executed(trade: Trade, correlation_id: str):
        payload = asdict(trade)

        payload["price"] = str(trade.price)
        payload["timestamp"] = trade.timestamp.isoformat()

        return EventEnvelope(
            event_id=str(uuid4()),
            event_type="TradeExecuted",
            schema_version=1,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            correlation_id=correlation_id,
            idempotency_key=f"trade:{trade.trade_id}",
            payload=payload
        )
