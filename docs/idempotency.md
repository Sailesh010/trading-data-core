# Financial event idempotency

Redis has one responsibility in this system: atomically claim an event's
`EventEnvelope.idempotency_key` before financial side effects occur. The Redis
adapter uses `SET key value NX`, rather than a racy read followed by a write.

Claims are permanent by default. This is the safest option for financial
replays, but requires a retention and archival policy as key volume grows. A
bounded TTL can control storage when the upstream replay horizon is known; it
also means a sufficiently old event can be processed again. Production TTLs
must therefore be longer than every broker retention, retry, and backfill
window. Processing failures release the claim so a retry can proceed. Redis
failures fail closed: no financial side effect is attempted when uniqueness
cannot be established.
