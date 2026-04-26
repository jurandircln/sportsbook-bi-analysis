-- Tabela Silver: apostas com tipos corretos, gross revenue e flag live
-- Regras de negócio aplicadas:
--   gross_revenue = turnover - winnings
--   is_live = placed_at >= event_start_time (aposta feita após início do evento)
-- Fonte: bronze.sportsbook + silver.events (para event_start_time)
CREATE TABLE IF NOT EXISTS silver.sportsbook (
    bet_id         TEXT         PRIMARY KEY,
    bet_type       VARCHAR(100),
    market         VARCHAR(100),
    customer_id    INTEGER      NOT NULL,
    settled_at     TIMESTAMP,
    placed_at      TIMESTAMP    NOT NULL,
    channel        VARCHAR(50),
    event_id       INTEGER,
    turnover       NUMERIC(12,2) NOT NULL,
    winnings       NUMERIC(12,2) NOT NULL,
    gross_revenue  NUMERIC(12,2) NOT NULL,
    is_live        BOOLEAN       NOT NULL,
    ingested_at    TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_sportsbook_customer
    ON silver.sportsbook (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_sportsbook_placed_at
    ON silver.sportsbook (placed_at);
CREATE INDEX IF NOT EXISTS idx_silver_sportsbook_event
    ON silver.sportsbook (event_id);
