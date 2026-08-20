with ledger_by_reference as (
    select
        reference,
        sum(debit_amount) as ledger_debit_amount,
        sum(credit_amount) as ledger_credit_amount
    from {{ ref('int_ledger_activity') }}
    group by 1
)

select
    trades.trade_id,
    trades.symbol,
    trades.executed_at,
    trades.trade_notional,
    coalesce(ledger.ledger_debit_amount, 0) as ledger_debit_amount,
    coalesce(ledger.ledger_credit_amount, 0) as ledger_credit_amount,
    trades.trade_notional - coalesce(ledger.ledger_debit_amount, 0) as notional_variance,
    case
        when ledger.reference is null then 'MISSING_LEDGER'
        when ledger.ledger_debit_amount <> ledger.ledger_credit_amount then 'UNBALANCED_LEDGER'
        when trades.trade_notional <> ledger.ledger_debit_amount then 'NOTIONAL_MISMATCH'
        else 'RECONCILED'
    end as reconciliation_status
from {{ ref('int_trade_notionals') }} as trades
left join ledger_by_reference as ledger
    on trades.ledger_reference = ledger.reference
