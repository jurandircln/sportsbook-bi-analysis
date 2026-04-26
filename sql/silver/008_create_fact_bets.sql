-- Tabela Fato Silver: apostas liquidadas
-- Grão: 1 linha por aposta
-- Regras de negócio aplicadas:
--   gross_revenue = turnover - winnings
--   is_live = placed_at >= event_start_time (via JOIN com dim_event na transformação)
--   placed_hour: dimensão degenerada (EXTRACT(HOUR FROM placed_at))
-- Fonte: bronze.sportsbook + silver.dim_event (para is_live)
CREATE TABLE IF NOT EXISTS silver.fact_bets (
    bet_id        TEXT          PRIMARY KEY,
    customer_id   INTEGER       NOT NULL,
    event_id      INTEGER,
    date_id       INTEGER       NOT NULL,
    market_id     INTEGER,
    channel_id    INTEGER,
    placed_at     TIMESTAMP     NOT NULL,
    settled_at    TIMESTAMP,
    placed_hour   INTEGER,
    turnover      NUMERIC(12,2) NOT NULL,
    winnings      NUMERIC(12,2) NOT NULL,
    gross_revenue NUMERIC(12,2) NOT NULL,
    is_live       BOOLEAN       NOT NULL,
    ingested_at   TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_customer
    ON silver.fact_bets (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_event
    ON silver.fact_bets (event_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_date
    ON silver.fact_bets (date_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_placed_at
    ON silver.fact_bets (placed_at);
