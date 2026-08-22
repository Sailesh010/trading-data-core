select
    journal_id,
    reference,
    account,
    min(posted_at) as posted_at,
    sum(case when direction = 'DEBIT' then amount else 0 end) as debit_amount,
    sum(case when direction = 'CREDIT' then amount else 0 end) as credit_amount,
    sum(case when direction = 'DEBIT' then amount else -amount end) as net_amount
from {{ ref('stg_operational__ledger_entries') }}
group by 1, 2, 3
