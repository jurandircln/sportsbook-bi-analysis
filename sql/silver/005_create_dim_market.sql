-- Tabela Dimensão Silver: mercado de aposta
-- Surrogate key (SERIAL): valores originais são texto livre sem unicidade garantida.
-- Dedupado por combinação única de (market_name, bet_type) na transformação.
-- Fonte: bronze.sportsbook
CREATE TABLE IF NOT EXISTS silver.dim_market (
    market_id    SERIAL       PRIMARY KEY,
    market_name  VARCHAR(100) NOT NULL,
    bet_type     VARCHAR(100),
    ingested_at  TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_silver_dim_market_unique
    ON silver.dim_market (market_name, bet_type);
