from dataclasses import dataclass
from decimal import Decimal
from typing import List

from src.models import Trade
from src.ledger import LedgerEntry


@dataclass
class ReconciliationException:
    trade_id: int
    expected_notional: Decimal
    ledger_notional: Decimal


def reconcile_trades_to_ledger(
    trades: List[Trade],
    ledger_entries: List[LedgerEntry]
):

    exceptions = []

    for trade in trades:

        expected_notional = trade.price * trade.quantity
        reference = f"trade:{trade.trade_id}"

        ledger_notional = sum(
            (
                entry.amount
                for entry in ledger_entries
                if entry.reference == reference
                and entry.direction == "DEBIT"
            ),
            Decimal("0")
        )

        if expected_notional != ledger_notional:

            exceptions.append(
                ReconciliationException(
                    trade_id=trade.trade_id,
                    expected_notional=expected_notional,
                    ledger_notional=ledger_notional
                )
            )

    return exceptions
