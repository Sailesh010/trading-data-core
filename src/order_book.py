class OrderBook:
    def __init__(self):
        self.bids = []  # list of (price, quantity)
        self.asks = []  # list of (price, quantity)

    def add_order(self, side, price, quantity):
        if side == "BUY":
            self.bids.append((price, quantity))
            self.bids.sort(reverse=True)
        else:
            self.asks.append((price, quantity))
            self.asks.sort()

    def match_buy(self, quantity):
        trades = []

        while quantity > 0 and self.asks:
            ask_price, ask_qty = self.asks[0]
            traded_qty = min(quantity, ask_qty)

            trades.append((ask_price, traded_qty))

            quantity -= traded_qty
            ask_qty -= traded_qty

            if ask_qty == 0:
                self.asks.pop(0)
            else:
                self.asks[0] = (ask_price, ask_qty)

        return trades
    