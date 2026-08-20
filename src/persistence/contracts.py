from __future__ import annotations

from types import TracebackType
from typing import Protocol, Sequence

from src.ledger import LedgerEntry
from src.models import Trade


class TradeRepository(Protocol):
    def add(self, trade: Trade) -> None: ...

    def get(self, trade_id: int) -> Trade | None: ...


class LedgerRepository(Protocol):
    def add_all(self, entries: Sequence[LedgerEntry]) -> None: ...

    def for_reference(self, reference: str) -> list[LedgerEntry]: ...


class UnitOfWork(Protocol):
    trades: TradeRepository
    ledger: LedgerRepository

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
