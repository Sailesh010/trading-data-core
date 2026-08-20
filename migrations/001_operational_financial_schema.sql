BEGIN;

CREATE TABLE trades (
    trade_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    symbol VARCHAR(16) NOT NULL CHECK (symbol = UPPER(symbol) AND length(symbol) > 0),
    side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    price NUMERIC(20, 8) NOT NULL CHECK (price > 0),
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    executed_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_trades_order_id ON trades (order_id);
CREATE INDEX idx_trades_symbol_executed_at ON trades (symbol, executed_at DESC);

CREATE TABLE ledger_entries (
    entry_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    journal_id VARCHAR(128) NOT NULL,
    account VARCHAR(128) NOT NULL,
    direction VARCHAR(6) NOT NULL CHECK (direction IN ('DEBIT', 'CREDIT')),
    amount NUMERIC(20, 8) NOT NULL CHECK (amount > 0),
    reference VARCHAR(128) NOT NULL,
    posted_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_ledger_posting UNIQUE (journal_id, account, direction)
);

CREATE INDEX idx_ledger_reference ON ledger_entries (reference);
CREATE INDEX idx_ledger_account_posted_at ON ledger_entries (account, posted_at DESC);

COMMIT;
