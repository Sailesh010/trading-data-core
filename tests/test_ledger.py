from datetime import datetime ,timezone
from decimal import Decimal

from src.models import Trade
from src.ledger import Ledger


def test_trade_creates_balanced_ledger():

    trade = Trade(
        trade_id=1,
        order_id=100,
        symbol="AAPL",
        side="BUY",
        price=Decimal("100.00"),
        quantity=5,
        timestamp=datetime.now(timezone.utc)
    )

    ledger = Ledger()

    ledger.post_trade(trade)

    debits = sum(
        entry.amount
        for entry in ledger.entries
        if entry.direction == "DEBIT"
    )

    credits = sum(
        entry.amount
        for entry in ledger.entries
        if entry.direction == "CREDIT"
    )

    assert debits == Decimal("500.00")
    assert credits == Decimal("500.00")
