from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

from src.events import EventEnvelope
from src.idempotency import IdempotencyStore
from src.models import Trade
from src.services.trade_posting import TradePostingService


@dataclass(frozen=True)
class ProcessingResult:
    processed: bool
    reason: str


class TradeExecutedProcessor:
    def __init__(
        self,
        idempotency_store: IdempotencyStore,
        posting_service: TradePostingService,
        *,
        claim_ttl_seconds: int | None = None,
    ):
        self._idempotency_store = idempotency_store
        self._posting_service = posting_service
        self._claim_ttl_seconds = claim_ttl_seconds

    def process(self, event: EventEnvelope) -> ProcessingResult:
        if event.event_type != "TradeExecuted":
            raise ValueError(f"unsupported event type: {event.event_type}")

        claimed = self._idempotency_store.claim(
            event.idempotency_key,
            ttl_seconds=self._claim_ttl_seconds,
        )
        if not claimed:
            return ProcessingResult(False, "duplicate")

        try:
            payload = event.payload
            trade = Trade(
                trade_id=int(payload["trade_id"]),
                order_id=int(payload["order_id"]),
                symbol=str(payload["symbol"]),
                side=str(payload["side"]),
                price=Decimal(str(payload["price"])),
                quantity=int(payload["quantity"]),
                timestamp=datetime.fromisoformat(str(payload["timestamp"])),
            )
            self._posting_service.post(trade)
        except Exception:
            self._idempotency_store.release(event.idempotency_key)
            raise

        return ProcessingResult(True, "processed")
