from datetime import datetime, timezone
from uuid import uuid4

from src.models import Order, Trade
from src.order_book import OrderBook
from src.events import EventEnvelope


class TradingEngine:

    def __init__(self):
        self.order_book = OrderBook()
        self.trades = []
        self.events = []
        self.trade_id_counter = 1

    def place_limit_order(self, order: Order):

        self.order_book.add_order(
            side=order.side,
            price=order.price,
            quantity=order.quantity
        )

        order.status = "OPEN"

        return order

    def place_market_buy_order(self, order: Order):

        executions = self.order_book.match_buy(order.quantity)

        correlation_id = str(uuid4())

        for price, qty in executions:

            trade = Trade(
                trade_id=self.trade_id_counter,
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                price=price,
                quantity=qty,
                timestamp=datetime.now(timezone.utc)
            )

            self.trades.append(trade)

            event = EventEnvelope.trade_executed(
                trade=trade,
                correlation_id=correlation_id
            )

            self.events.append(event)

            self.trade_id_counter += 1
            order.filled_qty += qty

        if order.filled_qty == order.quantity:
            order.status = "FILLED"
        else:
            order.status = "PARTIAL"

        return order
