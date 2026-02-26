from datetime import datetime
from src.models import Order, Trade
from src.order_book import OrderBook


class TradingEngine:
    def __init__(self):
        self.order_book = OrderBook()
        self.trades = []
        self.trade_id_counter = 1

    def place_limit_order(self, order: Order):
        """
        Adds a LIMIT order to the order book.
        """
        self.order_book.add_order(
            side=order.side,
            price=order.price,
            quantity=order.quantity
        )
        order.status = "OPEN"
        return order

    def place_market_buy_order(self, order: Order):
        """
        Executes a MARKET BUY order against the order book.
        """
        executions = self.order_book.match_buy(order.quantity)

        for price, qty in executions:
            trade = Trade(
                trade_id=self.trade_id_counter,
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                price=price,
                quantity=qty,
                timestamp=datetime.utcnow()
            )
            self.trades.append(trade)
            self.trade_id_counter += 1
            order.filled_qty += qty

        if order.filled_qty == order.quantity:
            order.status = "FILLED"
        else:
            order.status = "PARTIAL"

        return order
    