select
    trade_id,
    order_id,
    symbol,
    side,
    price,
    quantity,
    cast(price * quantity as numeric(28, 8)) as trade_notional,
    executed_at,
    'trade:' || cast(trade_id as text) as ledger_reference
from {{ ref('stg_operational__trades') }}
