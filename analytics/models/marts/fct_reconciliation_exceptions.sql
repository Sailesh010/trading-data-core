select *
from {{ ref('fct_reconciliation_status') }}
where reconciliation_status <> 'RECONCILED'
