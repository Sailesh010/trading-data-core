# Trading Data Core

A deterministic financial-data engineering project focused on the controls that matter in transaction systems: **correctness, traceability, reconciliation, idempotency-ready event design, and automated testing**.

This is an independent portfolio project using synthetic data only. It does not contain employer, client, or proprietary production code.

---

## Why I Built This

Financial systems need more than pipelines that simply move data.

A reliable platform should be able to answer:

- What transaction occurred?
- What event represented that transaction?
- Can the result be reproduced deterministically?
- Were the financial postings balanced?
- Can transaction activity be reconciled against the ledger?
- Can engineering changes be validated automatically before release?

Trading Data Core is being developed around those engineering principles.

---

## Current Architecture

```mermaid
flowchart LR
    A[Order] --> B[Deterministic Matching Engine]
    B --> C[Trade]
    C --> D[TradeExecuted Event]
    C --> E[Double-Entry Ledger]
    E --> F[Reconciliation Control]
    D --> G[Downstream Event Consumers - Future]
    F --> H[Reconciliation Exceptions]

    I[Pytest Test Suite] --> J[GitHub Actions CI]
