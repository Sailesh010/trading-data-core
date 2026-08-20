# Platform architecture decisions

## Boundary map

| Boundary | Owns | Does not own |
|---|---|---|
| Financial domain | Trade facts, balanced journals, reconciliation math | SQL, Redis, brokers, AWS |
| Persistence | Repository contracts, parameterized SQL, transactions | Matching or retry policy |
| Idempotency | Atomic claim/release decisions | General caching or ledger writes |
| Event transport | Wire format, metadata, retries, DLQ delivery | Financial calculations |
| Analytics | Downstream lineage, reporting, data-quality assertions | Operational transaction processing |
| Infrastructure | Undeployed AWS resource definitions | Application behavior or claimed runtime state |

## Transaction and delivery boundary

The synchronous posting service persists a trade and both journal entries in
one unit of work. The consumer claims the event key before invoking that
service. This provides replay safety for successful processing and permits a
retry after an application failure by releasing the claim.

There is still a real distributed-systems boundary between Redis and
PostgreSQL: a process can fail after the PostgreSQL commit but before the
success path completes. Database uniqueness prevents a second financial post,
but a production design should evaluate a transactional inbox table (or an
equivalent atomic database-owned deduplication record) and a transactional
outbox from matching to Kafka. The current code deliberately exposes this
tradeoff rather than claiming exactly-once delivery.

## Operational data model

`trades.trade_id` is the immutable financial fact key. Monetary columns are
`NUMERIC(20, 8)` and timestamps are `TIMESTAMPTZ`. Ledger entries use a database
identity key for row identity and a unique `(journal_id, account, direction)`
business constraint to prevent duplicate postings. Reference and time indexes
support reconciliation and account-history access; order and symbol/time
indexes support operational trade lookup.

## Retry classification

Malformed schema and business validation failures are non-retryable. Explicit
transient processing failures and inability to reach the idempotency store are
retryable. After the configured attempts, the original bytes and transport
headers enter the DLQ with error and attempt metadata. Logging hooks receive
identifiers, correlation IDs, idempotency keys, outcomes, and error classes;
they intentionally avoid financial payloads and secrets.

## Analytics boundary

dbt reads committed operational records. Staging models normalize types and
values, intermediate models calculate notionals and ledger activity, and marts
serve trade activity, postings, reconciliation status, and exception queues.
This can detect inconsistencies but cannot repair or authorize financial state.

## Deployment decision record

Amazon MSK is preferred over Kinesis because the application defines a Kafka
adapter and needs consumer-group replay semantics. RDS PostgreSQL is the source
of durable operational truth. ElastiCache Redis is used only for low-latency
atomic claims. CloudWatch receives infrastructure metrics/broker logs, while
IAM and security groups constrain runtime access. The definitions are not a
claim of a deployed or production-ready AWS estate.

## Review gates before a real deployment

- Choose transactional inbox/outbox semantics and offset-commit ordering.
- Threat-model secret delivery and rotate Redis/RDS credentials.
- Review accounting rules and account ownership with a qualified domain owner.
- Validate Terraform against the selected AWS provider and organization rules.
- Establish MSK topic configuration, retention, partitions, quotas, and DLQ.
- Add backup restore, failover, replay, and reconciliation runbooks.
- Define SLOs, alert routing, budgets, data retention, and access reviews.
