-- Tabela Dimensão Silver: canal de aposta
-- Surrogate key (SERIAL): valores originais são texto livre.
-- Dedupado por channel_name na transformação.
-- Fonte: bronze.sportsbook
CREATE TABLE IF NOT EXISTS silver.dim_channel (
    channel_id    SERIAL      PRIMARY KEY,
    channel_name  VARCHAR(50) NOT NULL,
    ingested_at   TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_silver_dim_channel_unique
    ON silver.dim_channel (channel_name);
