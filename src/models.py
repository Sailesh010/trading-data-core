from dataclasses import dataclass
from datetime import datetime


@dataclass
class Order:
    order_id: int
    user_id: int
    symbol: str
    side: str
    from decimal import Decimal
    price: Decimal | None
    quantity: int
    filled_qty: int
    status: str
    timestamp: datetime


@dataclass
class Trade:
    trade_id: int
    order_id: int
    symbol: str
    side: str
    price: float
    quantity: int
    timestamp: datetime
    
