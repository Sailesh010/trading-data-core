-- A reconciled trade cannot carry a non-zero trade-to-ledger variance.
select trade_id, notional_variance
from {{ ref('fct_reconciliation_status') }}
where reconciliation_status = 'RECONCILED'
  and notional_variance <> 0
