from datetime import datetime
from decimal import Decimal

from src.models import Trade
from src.ledger import Ledger
from src.reconciliation import reconcile_trades_to_ledger


def test_trade_reconciles_with_ledger():

    trade = Trade(
        trade_id=1,
        order_id=100,
        symbol="AAPL",
        side="BUY",
        price=Decimal("100.00"),
        quantity=5,
        timestamp=datetime.utcnow()
    )

    ledger = Ledger()

    ledger.post_trade(trade)

    exceptions = reconcile_trades_to_ledger(
        [trade],
        ledger.entries
    )

    assert len(exceptions) == 0
