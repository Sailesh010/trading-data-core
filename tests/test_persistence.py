from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.models import Trade
from src.persistence.memory import InMemoryUnitOfWork
from src.services.trade_posting import TradePostingService


def trade(trade_id: int = 1) -> Trade:
    offset = timezone(timedelta(hours=5, minutes=30))
    return Trade(trade_id, 100, "AAPL", "BUY", Decimal("100.12345678"), 5,
                 datetime(2026, 1, 2, 3, 4, 5, tzinfo=offset))


def test_trade_and_ledger_repository_contracts_preserve_financial_types():
    unit_of_work = InMemoryUnitOfWork()
    TradePostingService(lambda: unit_of_work).post(trade())

    stored = unit_of_work.trades.get(1)
    entries = unit_of_work.ledger.for_reference("trade:1")

    assert stored is not None
    assert stored.price == Decimal("100.12345678")
    assert stored.timestamp.utcoffset() == timedelta(hours=5, minutes=30)
    assert [entry.amount for entry in entries] == [Decimal("500.61728390")] * 2
    assert all(entry.posted_at.tzinfo is not None for entry in entries)


def test_unit_of_work_rolls_back_trade_when_ledger_write_fails():
    unit_of_work = InMemoryUnitOfWork()

    class FailingLedger:
        def add_all(self, entries):
            raise RuntimeError("ledger unavailable")

        def for_reference(self, reference):
            return []

    original_ledger = unit_of_work.ledger
    unit_of_work.ledger = FailingLedger()
    with pytest.raises(RuntimeError, match="ledger unavailable"):
        TradePostingService(lambda: unit_of_work).post(trade())

    assert unit_of_work.trades.get(1) is None
    unit_of_work.ledger = original_ledger


def test_duplicate_trade_is_rejected_without_duplicate_ledger_entries():
    unit_of_work = InMemoryUnitOfWork()
    service = TradePostingService(lambda: unit_of_work)
    service.post(trade())

    with pytest.raises(ValueError, match="already exists"):
        service.post(trade())

    assert len(unit_of_work.ledger.for_reference("trade:1")) == 2
