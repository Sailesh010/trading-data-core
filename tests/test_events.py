from datetime import datetime, timezone
from decimal import Decimal

from src.engine import TradingEngine
from src.models import Order


def test_trade_execution_creates_versioned_event():

    engine = TradingEngine()

    sell_order = Order(
        order_id=1,
        user_id=101,
        symbol="AAPL",
        side="SELL",
        price=Decimal("100.00"),
        quantity=10,
        filled_qty=0,
        status="NEW",
        timestamp=datetime.now(timezone.utc)
    )

    engine.place_limit_order(sell_order)

    buy_order = Order(
        order_id=2,
        user_id=201,
        symbol="AAPL",
        side="BUY",
        price=None,
        quantity=5,
        filled_qty=0,
        status="NEW",
        timestamp=datetime.now(timezone.utc)
    )

    engine.place_market_buy_order(buy_order)

    assert len(engine.events) == 1

    event = engine.events[0]

    assert event.event_type == "TradeExecuted"
    assert event.schema_version == 1
    assert event.idempotency_key == "trade:1"
    assert event.payload["symbol"] == "AAPL"
