-- Tabela Silver: tentativas de cash out com tipos corretos
-- Fonte: bronze.cashouts
CREATE TABLE IF NOT EXISTS silver.cashouts (
    bet_id          TEXT         NOT NULL,
    cashout_id      TEXT         PRIMARY KEY,
    created_at      TIMESTAMP    NOT NULL,
    status          VARCHAR(50)  NOT NULL,
    cashout_amount  NUMERIC(12,2),
    ingested_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_cashouts_bet
    ON silver.cashouts (bet_id);
