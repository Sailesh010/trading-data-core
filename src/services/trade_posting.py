from collections.abc import Callable

from src.ledger import Ledger
from src.models import Trade
from src.persistence.contracts import UnitOfWork


class TradePostingService:
    def __init__(self, unit_of_work_factory: Callable[[], UnitOfWork]):
        self._unit_of_work_factory = unit_of_work_factory

    def post(self, trade: Trade) -> None:
        journal = Ledger().post_trade(trade)
        with self._unit_of_work_factory() as unit_of_work:
            unit_of_work.trades.add(trade)
            unit_of_work.ledger.add_all(journal)
            unit_of_work.commit()
