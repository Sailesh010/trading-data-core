from __future__ import annotations

from copy import deepcopy
from types import TracebackType
from typing import Sequence

from src.ledger import LedgerEntry
from src.models import Trade


class InMemoryTradeRepository:
    def __init__(self, records: dict[int, Trade] | None = None):
        self._records = records if records is not None else {}

    def add(self, trade: Trade) -> None:
        if trade.trade_id in self._records:
            raise ValueError(f"trade {trade.trade_id} already exists")
        self._records[trade.trade_id] = trade

    def get(self, trade_id: int) -> Trade | None:
        return self._records.get(trade_id)


class InMemoryLedgerRepository:
    def __init__(self, records: list[LedgerEntry] | None = None):
        self._records = records if records is not None else []

    def add_all(self, entries: Sequence[LedgerEntry]) -> None:
        existing = {(entry.journal_id, entry.account, entry.direction) for entry in self._records}
        for entry in entries:
            key = (entry.journal_id, entry.account, entry.direction)
            if key in existing:
                raise ValueError(f"ledger posting {key!r} already exists")
            existing.add(key)
            self._records.append(entry)

    def for_reference(self, reference: str) -> list[LedgerEntry]:
        return [entry for entry in self._records if entry.reference == reference]


class InMemoryUnitOfWork:
    """Deterministic transaction double used by services and unit tests."""

    def __init__(self):
        self._trade_records: dict[int, Trade] = {}
        self._ledger_records: list[LedgerEntry] = []
        self.trades = InMemoryTradeRepository(self._trade_records)
        self.ledger = InMemoryLedgerRepository(self._ledger_records)
        self._snapshot: tuple[dict[int, Trade], list[LedgerEntry]] | None = None
        self.committed = False

    def __enter__(self) -> "InMemoryUnitOfWork":
        self._snapshot = deepcopy((self._trade_records, self._ledger_records))
        self.committed = False
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None or not self.committed:
            self.rollback()

    def commit(self) -> None:
        self.committed = True
        self._snapshot = None

    def rollback(self) -> None:
        if self._snapshot is not None:
            trades, entries = self._snapshot
            self._trade_records.clear()
            self._trade_records.update(trades)
            self._ledger_records.clear()
            self._ledger_records.extend(entries)
        self._snapshot = None
        self.committed = False
