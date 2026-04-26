-- Tabela Fato Silver: tentativas de cash out
-- Grão: 1 linha por tentativa de cash out
-- bet_id e status são dimensões degeneradas (sem tabela própria).
-- Fonte: bronze.cashouts
CREATE TABLE IF NOT EXISTS silver.fact_cashouts (
    cashout_id      TEXT          PRIMARY KEY,
    bet_id          TEXT          NOT NULL,
    date_id         INTEGER       NOT NULL,
    created_at      TIMESTAMP     NOT NULL,
    status          VARCHAR(50)   NOT NULL,
    cashout_amount  NUMERIC(12,2),
    ingested_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_fact_cashouts_bet
    ON silver.fact_cashouts (bet_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_cashouts_date
    ON silver.fact_cashouts (date_id);
