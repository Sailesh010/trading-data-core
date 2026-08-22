select
    cast(trade_id as bigint) as trade_id,
    cast(order_id as bigint) as order_id,
    upper(trim(symbol)) as symbol,
    upper(trim(side)) as side,
    cast(price as numeric(20, 8)) as price,
    cast(quantity as bigint) as quantity,
    cast(executed_at as timestamptz) as executed_at
from {{ source('operational', 'trades') }}
