from __future__ import annotations

from types import TracebackType
from typing import Any, Sequence

from src.ledger import LedgerEntry
from src.models import Trade


class PostgresTradeRepository:
    def __init__(self, connection: Any):
        self._connection = connection

    def add(self, trade: Trade) -> None:
        self._connection.execute(
            """
            INSERT INTO trades
                (trade_id, order_id, symbol, side, price, quantity, executed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (trade.trade_id, trade.order_id, trade.symbol, trade.side,
             trade.price, trade.quantity, trade.timestamp),
        )

    def get(self, trade_id: int) -> Trade | None:
        row = self._connection.execute(
            """
            SELECT trade_id, order_id, symbol, side, price, quantity, executed_at
            FROM trades WHERE trade_id = %s
            """,
            (trade_id,),
        ).fetchone()
        return Trade(*row) if row else None


class PostgresLedgerRepository:
    def __init__(self, connection: Any):
        self._connection = connection

    def add_all(self, entries: Sequence[LedgerEntry]) -> None:
        with self._connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO ledger_entries
                    (journal_id, account, direction, amount, reference, posted_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [(entry.journal_id, entry.account, entry.direction, entry.amount,
                  entry.reference, entry.posted_at) for entry in entries],
            )

    def for_reference(self, reference: str) -> list[LedgerEntry]:
        rows = self._connection.execute(
            """
            SELECT journal_id, account, direction, amount, reference, posted_at
            FROM ledger_entries WHERE reference = %s ORDER BY entry_id
            """,
            (reference,),
        ).fetchall()
        return [LedgerEntry(*row) for row in rows]


class PostgresUnitOfWork:
    def __init__(self, connection_factory):
        self._connection_factory = connection_factory
        self._connection = None

    def __enter__(self) -> "PostgresUnitOfWork":
        self._connection = self._connection_factory()
        self.trades = PostgresTradeRepository(self._connection)
        self.ledger = PostgresLedgerRepository(self._connection)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            self._connection.close()

    def commit(self) -> None:
        self._connection.commit()

    def rollback(self) -> None:
        self._connection.rollback()
