-- Tabela Dimensão Silver: nível CRM por cliente por mês (variação temporal)
-- Regra de negócio: forward-fill aplicado — meses sem registro usam o nível mais recente.
-- Para JOIN na análise: customer_id + DATE_TRUNC('month', placed_at) = year_month
-- Fonte: bronze.customer_crm_level
CREATE TABLE IF NOT EXISTS silver.dim_crm_level (
    customer_id  INTEGER     NOT NULL,
    year_month   DATE        NOT NULL,
    crm_level    VARCHAR(50) NOT NULL,
    ingested_at  TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (customer_id, year_month)
);

CREATE INDEX IF NOT EXISTS idx_silver_dim_crm_level_customer
    ON silver.dim_crm_level (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_dim_crm_level_month
    ON silver.dim_crm_level (year_month);
