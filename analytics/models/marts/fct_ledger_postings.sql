select
    journal_id,
    reference,
    account,
    posted_at,
    debit_amount,
    credit_amount,
    net_amount
from {{ ref('int_ledger_activity') }}
