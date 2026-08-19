from dataclasses import dataclass
from decimal import Decimal
from typing import List

from src.models import Trade


@dataclass(frozen=True)
class LedgerEntry:
    journal_id: str
    account: str
    direction: str
    amount: Decimal
    reference: str


class Ledger:

    def __init__(self):
        self.entries: List[LedgerEntry] = []

    def post_trade(self, trade: Trade):

        amount = trade.price * trade.quantity

        journal_id = f"trade-{trade.trade_id}"
        reference = f"trade:{trade.trade_id}"

        journal = [
            LedgerEntry(
                journal_id=journal_id,
                account="customer_asset",
                direction="DEBIT",
                amount=amount,
                reference=reference
            ),
            LedgerEntry(
                journal_id=journal_id,
                account="broker_cash",
                direction="CREDIT",
                amount=amount,
                reference=reference
            )
        ]

        self._validate_balanced_journal(journal)

        self.entries.extend(journal)

    def _validate_balanced_journal(self, entries):

        debit_total = sum(
            (entry.amount for entry in entries if entry.direction == "DEBIT"),
            Decimal("0")
        )

        credit_total = sum(
            (entry.amount for entry in entries if entry.direction == "CREDIT"),
            Decimal("0")
        )

        if debit_total != credit_total:
            raise ValueError(
                f"Unbalanced journal: debit={debit_total}, credit={credit_total}"
            )
