# Deterministic Trading Data Core

This project implements a simplified, end-to-end trading data system
focused on correctness, determinism, and auditability.

## What it does
- Accepts limit and market orders
- Maintains an in-memory order book
- Matches orders deterministically
- Generates trades from executions
- Demonstrates real trading behavior (one order → multiple trades)

## Design Principles
- Orders represent intent
- Trades represent facts
- State is derived, not guessed
- No ML, no hype — correctness first

## Tech Stack
- Python
- Dataclasses
- Event-driven design
- In-memory state management

## Why this matters
This mirrors how real trading and brokerage systems
prioritize accuracy, replayability, and explainability
over dashboards or premature optimization.