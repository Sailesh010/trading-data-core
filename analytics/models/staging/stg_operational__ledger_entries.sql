select
    cast(entry_id as bigint) as entry_id,
    trim(journal_id) as journal_id,
    trim(account) as account,
    upper(trim(direction)) as direction,
    cast(amount as numeric(20, 8)) as amount,
    trim(reference) as reference,
    cast(posted_at as timestamptz) as posted_at
from {{ source('operational', 'ledger_entries') }}
