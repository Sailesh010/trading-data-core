select
    trade_id,
    order_id,
    symbol,
    side,
    quantity,
    price,
    trade_notional,
    executed_at
from {{ ref('int_trade_notionals') }}
