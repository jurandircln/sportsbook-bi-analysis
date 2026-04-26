-- Tabela Dimensão Silver: calendário por dia
-- Granularidade: 1 registro por dia. Gerada na transformação cobrindo o período
-- relevante (Jul/2017 a Set/2019, com margem para apostas pré-temporada).
-- Chave: YYYYMMDD como INTEGER (ex: 20180901).
-- placed_hour permanece em fact_bets como dimensão degenerada (não infla esta tabela).
-- Fonte: gerada programaticamente durante a transformação
CREATE TABLE IF NOT EXISTS silver.dim_date (
    date_id      INTEGER     PRIMARY KEY,
    full_date    DATE        NOT NULL,
    year         INTEGER     NOT NULL,
    month        INTEGER     NOT NULL,
    month_name   VARCHAR(20) NOT NULL,
    day          INTEGER     NOT NULL,
    day_of_week  INTEGER     NOT NULL,
    day_name     VARCHAR(20) NOT NULL,
    is_weekend   BOOLEAN     NOT NULL,
    ingested_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_dim_date_full_date
    ON silver.dim_date (full_date);
