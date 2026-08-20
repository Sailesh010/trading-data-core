-- Financial invariant: every journal's total debits must equal total credits.
select
    journal_id,
    sum(case when direction = 'DEBIT' then amount else 0 end) as debit_total,
    sum(case when direction = 'CREDIT' then amount else 0 end) as credit_total
from {{ ref('stg_operational__ledger_entries') }}
group by 1
having sum(case when direction = 'DEBIT' then amount else 0 end)
    <> sum(case when direction = 'CREDIT' then amount else 0 end)
