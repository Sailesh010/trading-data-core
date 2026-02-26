from datetime import datetime
from src.models import Order
from src.engine import TradingEngine

# Initialize engine
engine = TradingEngine()

# Add SELL limit orders (liquidity)
engine.place_limit_order(
    Order(
        order_id=1,
        user_id=101,
        symbol="AAPL",
        side="SELL",
        price=101.0,
        quantity=200,
        filled_qty=0,
        status="NEW",
        timestamp=datetime.utcnow()
    )
)

engine.place_limit_order(
    Order(
        order_id=2,
        user_id=102,
        symbol="AAPL",
        side="SELL",
        price=102.0,
        quantity=150,
        filled_qty=0,
        status="NEW",
        timestamp=datetime.utcnow()
    )
)

# Place MARKET BUY order
buy_order = Order(
    order_id=3,
    user_id=201,
    symbol="AAPL",
    side="BUY",
    price=None,
    quantity=250,
    filled_qty=0,
    status="NEW",
    timestamp=datetime.utcnow()
)

engine.place_market_buy_order(buy_order)

print("\n=== Trades Executed ===")
for trade in engine.trades:
    print(trade)

print("\nFinal Buy Order State:")
print(buy_order)

