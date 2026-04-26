-- Tabela Bronze: níveis CRM mensais por cliente
-- Fonte: Customer_crm_level.csv
-- ATENÇÃO: registros existem apenas nos meses de mudança de nível.
-- Para meses intermediários, aplicar forward-fill na camada Silver.
CREATE TABLE IF NOT EXISTS bronze.customer_crm_level (
    customer_id    TEXT,
    date_yearmonth TEXT,
    crm_level      TEXT,
    ingested_at    TIMESTAMP DEFAULT NOW()
);
