# dbt analytics project

This project transforms the PostgreSQL operational `trades` and
`ledger_entries` sources into staging views, intermediate financial logic, and
reporting marts. It is downstream analytics engineering only: dbt does not
participate in trade execution, idempotency, or transactional ledger posting.

Copy `profiles.yml.example` outside the repository to your dbt profiles
directory and supply its environment variables. Then run `dbt build` from this
directory against a PostgreSQL database containing the operational migration.
